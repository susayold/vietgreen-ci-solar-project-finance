"""Local/CI wrapper; derived project data is only materialized in CI artifacts."""
from analytics.validate_v5_current_surfaces import validate
from analytics.scan_stale_v4_content import scan
if __name__=="__main__":
    print(validate(".")); print(scan("."))
