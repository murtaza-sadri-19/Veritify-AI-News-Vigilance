# This file makes the services directory a Python package
# It can be empty or can expose specific functionality

from services.fact_check_service import FactCheckService

__all__ = ['FactCheckService']