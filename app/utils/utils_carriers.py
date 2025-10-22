import re
import logging

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