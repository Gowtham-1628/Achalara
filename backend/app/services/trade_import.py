"""Trade import service for handling CSV uploads"""
import csv
import io
import uuid
from typing import List, Dict
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from app.services.trade_ingestion import TradeValidator
from app.services.portfolio_calculation import PortfolioCalculationService
from app.models.client import Client
from app.models.account import Account
from app.models.trade import Trade
from app.models.strategy import Strategy
from app.models.sleeve import Sleeve
from app.models.sync_log import SyncLog


logger = logging.getLogger(__name__)


class TradeImportService:
    """Service for importing trades from CSV files"""

    def __init__(self, db: Session):
        self.db = db
        self.validator = TradeValidator()

    def _refresh_positions(self, sleeve_ids) -> None:
        """Recalculate and persist open/closed position rows for the given sleeves.

        Called after a successful IMPORT so the positions table reflects the new
        trades. Failures here are logged but never fail the import — positions
        are also computed live on read.
        """
        calc = PortfolioCalculationService(self.db)
        for sid in set(sleeve_ids):
            try:
                calc.persist_all_positions(sid)
            except Exception as e:  # noqa: BLE001
                self.db.rollback()
                logger.error(f"Failed to refresh positions for sleeve {sid}: {e}")

    def import_from_file(
        self,
        file_content: bytes,
        sleeve_id: str,
        mode: str = "IMPORT",
        import_type: str = "HISTORICAL",
    ) -> Dict:
        """
        Import trades from CSV file

        Args:
            file_content: CSV file bytes
            sleeve_id: Target sleeve ID
            mode: VALIDATE (dry run) or IMPORT (persist)

        Returns:
            {
                'success': bool,
                'total': int,
                'imported': int,
                'duplicates': int,
                'errors': List[str],
                'sync_log_id': str (if IMPORT mode)
            }
        """
        result = {
            "success": False,
            "total": 0,
            "imported": 0,
            "duplicates": 0,
            "errors": [],
            "sync_log_id": None,
        }

        try:
            # Verify sleeve exists
            sleeve = self.db.query(Sleeve).filter(Sleeve.id == sleeve_id).first()
            if not sleeve:
                result["errors"].append(f"Sleeve {sleeve_id} not found")
                return result

            # Parse CSV
            trades_data = self._parse_csv(file_content)
            result["total"] = len(trades_data)

            # Validate trades
            validation_result = self.validator.validate_batch(trades_data)
            valid_trades = validation_result["trades"]
            result["errors"].extend(validation_result["errors"])

            if not valid_trades:
                result["errors"].insert(0, "No valid trades found in CSV")
                return result

            # Get existing trades for deduplication
            existing_trades = (
                self.db.query(Trade).filter(Trade.sleeve_id == sleeve_id).all()
            )

            # Detect duplicates
            duplicate_indices = self.validator.detect_duplicates(
                valid_trades, existing_trades
            )
            result["duplicates"] = len(duplicate_indices)

            # Filter out duplicates
            trades_to_import = [
                trade
                for idx, trade in enumerate(valid_trades)
                if idx not in duplicate_indices
            ]

            result["imported"] = len(trades_to_import)

            # If VALIDATE mode, stop here
            if mode == "VALIDATE":
                result["success"] = True
                return result

            # IMPORT mode: persist to database
            if mode == "IMPORT":
                sync_log = SyncLog(
                    import_type=import_type,
                    status="IN_PROGRESS",
                    rows_processed=result["total"],
                    rows_success=0,
                    rows_failed=result["duplicates"] + len(validation_result["errors"]),
                )
                self.db.add(sync_log)
                self.db.flush()  # Get sync_log ID before committing
                result["sync_log_id"] = sync_log.id

                try:
                    # Persist trades
                    for trade_data in trades_to_import:
                        # Convert trade_date string to date object
                        trade_date = datetime.strptime(
                            trade_data.trade_date, "%Y-%m-%d"
                        ).date()

                        trade = Trade(
                            sleeve_id=sleeve_id,
                            trade_date=trade_date,
                            symbol=trade_data.symbol,
                            action=trade_data.action,
                            quantity=Decimal(str(trade_data.quantity)),
                            price=Decimal(str(trade_data.price)),
                            commission=Decimal(str(trade_data.commission)),
                            notes=trade_data.notes,
                        )
                        self.db.add(trade)

                    # Update sync log
                    sync_log.rows_success = result["imported"]
                    sync_log.status = "SUCCESS"

                    self.db.commit()
                    result["success"] = True
                    logger.info(
                        f"Successfully imported {result['imported']} trades "
                        f"for sleeve {sleeve_id}"
                    )
                    self._refresh_positions([sleeve_id])

                except IntegrityError as e:
                    self.db.rollback()
                    sync_log.status = "FAILED"
                    sync_log.error_details = str(e)
                    result["errors"].append(f"Database error: {str(e)}")
                    result["imported"] = 0
                    logger.error(f"Import failed with database error: {e}")

                except Exception as e:
                    self.db.rollback()
                    sync_log.status = "FAILED"
                    sync_log.error_details = str(e)
                    result["errors"].append(f"Unexpected error: {str(e)}")
                    result["imported"] = 0
                    logger.error(f"Import failed: {e}")

            return result

        except Exception as e:
            result["errors"].append(f"Import error: {str(e)}")
            logger.error(f"Import error: {e}")
            return result

    def import_routed(
        self,
        file_content: bytes,
        client_id: str,
        mode: str = "IMPORT",
        import_type: str = "HISTORICAL",
    ) -> Dict:
        """
        Import trades and auto-route each row to the right account + strategy.

        Resolves the Account (by ``account_number`` = the CSV ``Account`` column),
        the global Strategy (by name = the CSV ``Strategy`` column), and the Sleeve
        linking the two, creating any that are missing (only in IMPORT mode). Dedup
        is applied per sleeve. Supports files that span multiple accounts/strategies.

        Returns the standard result dict plus ``accounts_created``,
        ``strategies_created`` (new global strategy definitions) and
        ``sleeves_created`` (new account x strategy links). In VALIDATE these are the
        counts that *would* be created.
        """
        result = {
            "success": False,
            "total": 0,
            "imported": 0,
            "duplicates": 0,
            "errors": [],
            "sync_log_id": None,
            "accounts_created": 0,
            "strategies_created": 0,
            "sleeves_created": 0,
        }

        try:
            client = self.db.query(Client).filter(Client.id == client_id).first()
            if not client:
                result["errors"].append(f"Client {client_id} not found")
                return result

            trades_data = self._parse_csv(file_content)
            result["total"] = len(trades_data)

            validation_result = self.validator.validate_batch(trades_data)
            valid_trades = validation_result["trades"]
            result["errors"].extend(validation_result["errors"])

            # Every routable row needs both an Account and a Strategy value
            routable = []
            for t in valid_trades:
                if not t.account:
                    result["errors"].append(
                        f"{t.symbol} {t.trade_date}: missing Account for auto-route"
                    )
                elif not t.strategy:
                    result["errors"].append(
                        f"{t.symbol} {t.trade_date}: missing Strategy for auto-route"
                    )
                else:
                    routable.append(t)

            if not routable:
                result["errors"].insert(
                    0, "No trades have both Account and Strategy for routing"
                )
                return result

            create = mode == "IMPORT"
            account_cache: Dict[str, Account] = {}
            strategy_def_cache: Dict[str, Strategy] = {}
            sleeve_cache: Dict[tuple, Sleeve] = {}
            new_accounts: set = set()
            new_strategies: set = set()
            new_sleeves: set = set()
            seen_keys: Dict[str, set] = {}

            sync_log = None
            if create:
                sync_log = SyncLog(
                    import_type=import_type,
                    status="IN_PROGRESS",
                    rows_processed=result["total"],
                    rows_success=0,
                    rows_failed=result["duplicates"] + len(validation_result["errors"]),
                )
                self.db.add(sync_log)
                self.db.flush()
                result["sync_log_id"] = sync_log.id

            affected_sleeves = set()
            try:
                for t in routable:
                    account = self._resolve_account(
                        client_id, t.account, create, account_cache, new_accounts
                    )
                    sleeve = self._resolve_sleeve(
                        account,
                        t.account,
                        t.strategy,
                        create,
                        strategy_def_cache,
                        sleeve_cache,
                        new_strategies,
                        new_sleeves,
                    )

                    # Per-sleeve dedup bucket (seeded from existing DB trades)
                    bucket = (
                        sleeve.id
                        if sleeve is not None
                        else f"NEW::{t.account}::{t.strategy.lower()}"
                    )
                    if bucket not in seen_keys:
                        seen_keys[bucket] = self._existing_keys(sleeve)

                    key = self._dedup_key(t.trade_date, t.symbol, t.quantity, t.price)
                    if key in seen_keys[bucket]:
                        result["duplicates"] += 1
                        continue
                    seen_keys[bucket].add(key)

                    result["imported"] += 1
                    if create:
                        affected_sleeves.add(sleeve.id)
                        self.db.add(
                            Trade(
                                sleeve_id=sleeve.id,
                                trade_date=datetime.strptime(
                                    t.trade_date, "%Y-%m-%d"
                                ).date(),
                                symbol=t.symbol,
                                action=t.action,
                                quantity=Decimal(str(t.quantity)),
                                price=Decimal(str(t.price)),
                                commission=Decimal(str(t.commission)),
                                notes=t.notes,
                            )
                        )

                result["accounts_created"] = len(new_accounts)
                result["strategies_created"] = len(new_strategies)
                result["sleeves_created"] = len(new_sleeves)

                if create:
                    sync_log.rows_success = result["imported"]
                    sync_log.rows_failed = result["duplicates"] + len(
                        validation_result["errors"]
                    )
                    sync_log.status = "SUCCESS"
                    self.db.commit()
                    logger.info(
                        f"Routed import: {result['imported']} trades into "
                        f"{result['strategies_created']} new / existing strategies "
                        f"for client {client_id}"
                    )
                    self._refresh_positions(affected_sleeves)

                result["success"] = True
                return result

            except (IntegrityError, Exception) as e:
                self.db.rollback()
                if sync_log is not None:
                    sync_log.status = "FAILED"
                    sync_log.error_details = str(e)
                    self.db.commit()
                result["errors"].append(f"Routed import error: {str(e)}")
                result["imported"] = 0
                logger.error(f"Routed import failed: {e}")
                return result

        except Exception as e:
            result["errors"].append(f"Import error: {str(e)}")
            logger.error(f"Routed import error: {e}")
            return result

    def _resolve_account(
        self, client_id, account_number, create, cache, new_accounts
    ) -> Account | None:
        """Find an account by number within a client, creating it if missing."""
        if account_number in cache:
            return cache[account_number]
        account = (
            self.db.query(Account)
            .filter(
                Account.client_id == client_id,
                Account.account_number == account_number,
            )
            .first()
        )
        if account is None and create:
            account = Account(
                id=str(uuid.uuid4()),
                client_id=client_id,
                account_number=account_number,
                name=f"Account {account_number}",
                description="Auto-created during import",
            )
            self.db.add(account)
            self.db.flush()
            new_accounts.add(account_number)
        elif account is None:
            new_accounts.add(account_number)  # VALIDATE: would be created
        cache[account_number] = account
        return account

    def _resolve_strategy_def(
        self, strategy_name, create, cache, new_strategies
    ) -> Strategy | None:
        """Find a firm-wide strategy definition by name (case-insensitive),
        creating it if missing. The first-seen casing is preserved on create."""
        key = strategy_name.lower()
        if key in cache:
            return cache[key]
        strategy = (
            self.db.query(Strategy).filter(func.lower(Strategy.name) == key).first()
        )
        if strategy is None and create:
            strategy = Strategy(
                id=str(uuid.uuid4()),
                name=strategy_name,
                description="Auto-created during import",
            )
            self.db.add(strategy)
            self.db.flush()
            new_strategies.add(key)
        elif strategy is None:
            new_strategies.add(key)  # VALIDATE: would be created
        cache[key] = strategy
        return strategy

    def _resolve_sleeve(
        self,
        account,
        account_number,
        strategy_name,
        create,
        strategy_def_cache,
        sleeve_cache,
        new_strategies,
        new_sleeves,
    ) -> Sleeve | None:
        """Find the sleeve linking ``account`` to the named strategy, creating the
        global strategy and/or the sleeve if missing. Strategy name is matched
        case-insensitively."""
        key = (account_number, strategy_name.lower())
        if key in sleeve_cache:
            return sleeve_cache[key]

        strategy = self._resolve_strategy_def(
            strategy_name, create, strategy_def_cache, new_strategies
        )

        sleeve = None
        if account is not None and strategy is not None:
            sleeve = (
                self.db.query(Sleeve)
                .filter(
                    Sleeve.account_id == account.id,
                    Sleeve.strategy_id == strategy.id,
                )
                .first()
            )
        if sleeve is None and create and account is not None and strategy is not None:
            sleeve = Sleeve(
                id=str(uuid.uuid4()),
                account_id=account.id,
                strategy_id=strategy.id,
            )
            self.db.add(sleeve)
            self.db.flush()
            new_sleeves.add(key)
        elif sleeve is None:
            new_sleeves.add(key)  # VALIDATE or new account/strategy: would be created
        sleeve_cache[key] = sleeve
        return sleeve

    def _existing_keys(self, sleeve) -> set:
        """Dedup keys for trades already persisted under a sleeve."""
        if sleeve is None or sleeve.id is None:
            return set()
        existing = self.db.query(Trade).filter(Trade.sleeve_id == sleeve.id).all()
        return {
            self._dedup_key(e.trade_date, e.symbol, float(e.quantity), float(e.price))
            for e in existing
        }

    @staticmethod
    def _dedup_key(trade_date, symbol, quantity, price) -> tuple:
        """Normalize a trade into a comparable key (date, symbol, qty, price)."""
        if isinstance(trade_date, str):
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        return (trade_date, str(symbol).upper(), float(quantity), float(price))

    def _parse_csv(self, file_content: bytes) -> List[Dict]:
        """Parse CSV file content"""
        try:
            content_str = file_content.decode("utf-8")
            reader = csv.DictReader(io.StringIO(content_str))

            if not reader.fieldnames:
                raise ValueError("CSV file is empty")

            rows = list(reader)
            return rows

        except UnicodeDecodeError:
            raise ValueError("File must be UTF-8 encoded CSV")
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {str(e)}")
