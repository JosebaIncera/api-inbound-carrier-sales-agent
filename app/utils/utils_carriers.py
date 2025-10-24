import re
import logging
from app.supabase import supabase

# Set up logger for this module
logger = logging.getLogger(__name__)

def validate_mc_format(mc_number: str) -> bool:
    """Valida que el MC number siga el formato 'MC XXXXXX'"""
    logger.debug(f"Validating MC format for: {mc_number}")
    
    try:
        # Patrón regex para validar formato MC seguido de 6 dígitos
        pattern = r'^MC\s\d{6}$'
        logger.debug(f"Using regex pattern: {pattern}")
        
        is_valid = bool(re.match(pattern, mc_number))
        logger.debug(f"MC format validation result: {is_valid}")
        
        if is_valid:
            logger.debug(f"MC number {mc_number} matches required format")
        else:
            logger.debug(f"MC number {mc_number} does not match required format 'MC XXXXXX'")
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Error validating MC format for {mc_number}: {str(e)}")
        return False

def extract_mc_digits(mc_number: str) -> str:
    """Extrae solo los dígitos del MC number (ej: 'MC 123456' -> '123456')"""
    logger.debug(f"Extracting MC digits from: {mc_number}")
    
    try:
        # Extraer solo los dígitos del MC number
        digits = re.sub(r'[^\d]', '', mc_number)
        logger.debug(f"Extracted MC digits: {digits}")
        
        return digits
        
    except Exception as e:
        logger.error(f"Error extracting MC digits from {mc_number}: {str(e)}")
        return ""

def check_carrier_exists(mc_digits: str) -> bool:
    """Verifica si existe un carrier con el MC number en la base de datos"""
    logger.debug(f"Checking if carrier exists with MC digits: {mc_digits}")
    
    try:
        # Query the carriers table for the MC number
        result = supabase.table("carriers").select("mc_number").eq("mc_number", mc_digits).execute()
        
        exists = len(result.data) > 0 if result.data else False
        logger.debug(f"Carrier exists check result: {exists}")
        
        if exists:
            logger.info(f"Found carrier with MC number: {mc_digits}")
        else:
            logger.info(f"No carrier found with MC number: {mc_digits}")
        
        return exists
        
    except Exception as e:
        logger.error(f"Error checking carrier existence for MC {mc_digits}: {str(e)}")
        return False