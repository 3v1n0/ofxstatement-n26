import logging

from decimal import Decimal
from enum import Enum
from typing import Any, Iterable, List, Optional

from ofxstatement.plugin import Plugin
from ofxstatement.parser import CsvStatementParser
from ofxstatement.statement import (
    BankAccount,
    Currency,
    Statement,
    StatementLine,
    generate_transaction_id,
    recalculate_balance,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("n26")

TYPE_MAPPING = {
    "Entrata": "XFER",
    "Pagamento MasterCard": "POS",
    "Trasferimento in uscita": "XFER",
    "N26 sponsorizzazione": "CREDIT",
    "MoneyBeam": "XFER",
    "Income": "XFER",
    "MasterCard Payment": "POS",
    "Outgoing Transfer": "XFER",
    "Direct Debit": "XFER",
    "Credit Transfer": "XFER",
    "Debit Transfer": "XFER",
    "Presentment": "POS",
    "Reward": "CREDIT",

    # Add translations for other statements
}


class N26Parser(CsvStatementParser):
    date_format = "%Y-%m-%d"

    mappings = {
        "date": 0,
        "date_user": 1,
        "payee": 2,
        "account_number": 3,
        "trntype": 4,
        "memo": 5,
        "account_name": 6,
        "amount": 7,
        "orig_amount": 8,
        "orig_currency": 9,
        "exchange_rate": 10,
    }

    def parse(self):
        statement = super().parse()
        recalculate_balance(statement)
        return statement

    def split_records(self):
        return [r for r in super().split_records()][1:]

    def strip_spaces(self, string: str) -> str:
        return " ".join(string.strip().split())

    def parse_value(self, value: Optional[str], field: str) -> Any:
        if field == "trntype":
            native_type = value.split(" - ", 1)[0].strip()
            trntype = TYPE_MAPPING.get(native_type)

            if not trntype:
                logger.warning(f"Mapping not found for {value}")
                return "OTHER"

            return trntype

        elif field == "orig_currency":
            return Currency(symbol=value)

        elif field == "memo":
            return self.strip_spaces(value)

        elif field == "payee":
            return self.strip_spaces(value)

        return super().parse_value(value, field)

    def parse_record(self, line: List[str]) -> Optional[StatementLine]:
        stmt_line = super().parse_record(line)

        if stmt_line.payee == 'N26 Bank' and 'mark-up fee' in stmt_line.memo:
            stmt_line.trntype = "FEE"
        elif stmt_line.payee == 'N26' and 'N26' in stmt_line.memo:
            stmt_line.trntype = "FEE"

        if not stmt_line.memo or stmt_line.memo == "-":
            stmt_line.memo = stmt_line.payee

        account_number = line[self.mappings["account_number"]]
        if account_number:
            if stmt_line.payee:
                stmt_line.payee += f' ({account_number})'
            else:
                stmt_line.payee = account_number

        account_name = line[self.mappings["account_name"]]
        if account_name:
            if stmt_line.payee:
                stmt_line.payee += f' - {account_name}'
            else:
                stmt_line.payee = account_name

        if stmt_line.orig_currency:
            exchange_rate = line[self.mappings["exchange_rate"]]
            if exchange_rate:
                stmt_line.orig_currency.rate = self.parse_float(exchange_rate)

        stmt_line.id = generate_transaction_id(stmt_line)
        logger.debug(stmt_line)
        return stmt_line


class N26Plugin(Plugin):
    """N26 parser"""

    def get_parser(self, filename: str) -> N26Parser:
        file = open(filename, "r", encoding='utf-8')
        parser = N26Parser(file)
        parser.statement.currency = self.settings.get("currency")
        parser.statement.account_id = self.settings.get("account")
        parser.statement.bank_id = self.settings.get("bank", "N26")
        return parser
