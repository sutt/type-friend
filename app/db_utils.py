import argparse
import os
import sys
from sqlalchemy import text

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import get_session, SuccessfulSpellIP

def list_ips():
    """Lists all IPs in the successful_spell_ips table."""
    session = get_session()
    try:
        ips = session.query(SuccessfulSpellIP).all()
        if not ips:
            print("No IPs found in the successful_spell_ips table.")
            return

        print(f"{'IP Address':<20} {'User UUID':<40} {'Cast Time':<30}")
        print("-" * 90)
        for ip in ips:
            print(f"{ip.ip:<20} {ip.user_uuid:<40} {str(ip.cast_time):<30}")
    finally:
        session.close()

def erase_ip(ip_address):
    """Erases an IP from the successful_spell_ips table."""
    session = get_session()
    try:
        record = session.query(SuccessfulSpellIP).filter_by(ip=ip_address).first()
        if record:
            session.delete(record)
            session.commit()
            print(f"Successfully erased IP address: {ip_address}")
        else:
            print(f"IP address not found: {ip_address}")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Devscripts DB Utils")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sub-parser for the list_ips command
    parser_list = subparsers.add_parser("list_ips", help="List all IPs in the successful_spell_ips table.")

    # Sub-parser for the erase_ip command
    parser_erase = subparsers.add_parser("erase_ip", help="Erase an IP from the successful_spell_ips table.")
    parser_erase.add_argument("ip_address", type=str, help="The IP address to erase.")

    args = parser.parse_args()

    if args.command == "list_ips":
        list_ips()
    elif args.command == "erase_ip":
        erase_ip(args.ip_address)
