# Changes Export to Excel

This directory contains scripts to export change detection data to Excel format for easy analysis and reporting.

## Files

- `export_changes_to_excel.py` - Main export script
- `export_changes_cli.py` - Command-line interface with advanced options
- `test_export_changes.py` - Test script with sample data
- `README_EXPORT.md` - This documentation

## Features

### Excel Export Script (`export_changes_to_excel.py`)

The main export script provides the following features:

- **Multi-site Support**: Exports changes for all active sites in your configuration
- **Separate Worksheets**: Each site gets its own worksheet in the Excel workbook
- **Professional Styling**: 
  - Blue header row with white text
  - Borders around all cells
  - Auto-adjusted column widths
  - Summary information at the top of each sheet
- **Comprehensive Data**: Includes all change information:
  - URL
  - Change Type (new_page, modified_content, deleted_page, ignored_file)
  - Detection Date & Time
  - Details
  - Previous Hash (for modified content)
  - New Hash (for new/modified content)
  - File Type (for ignored files)

## Usage

### Prerequisites

Install the required dependencies:

```bash
pip install pandas openpyxl
```

Or install all project dependencies:

```bash
pip install -r requirements.txt
```

### Basic Usage

1. **Export all changes to Excel**:
   ```bash
   cd scripts
   python export_changes_to_excel.py
   ```

2. **Advanced CLI with options**:
   ```bash
   cd scripts
   python export_changes_cli.py --help
   ```

3. **Export specific site**:
   ```bash
   python export_changes_cli.py --site "Judiciary UK"
   ```

4. **Export with custom filename**:
   ```bash
   python export_changes_cli.py --output "my_report.xlsx"
   ```

5. **Test with sample data**:
   ```bash
   cd scripts
   python test_export_changes.py
   ```

### Output

The script will:

1. Look for change files in the `changes/` directory
2. Find the most recent change file for each active site
3. Create an Excel workbook with separate sheets for each site
4. Save the file as `output/changes_export_YYYYMMDD_HHMMSS.xlsx`

### File Structure

```
changes/
├── Judiciary UK_20241201_143022_changes.json
├── Waverley Borough Council_20241201_143045_changes.json
└── ...

output/
└── changes_export_20241201_143100.xlsx
```

## Excel Output Format

Each worksheet contains:

### Summary Section (Rows 1-3)
- Site name
- Detection time
- Total number of changes

### Data Section (Rows 5+)
- **URL**: The webpage URL that changed
- **Change Type**: Type of change detected
  - `new_page`: New URL found in sitemap
  - `modified_content`: Content hash changed
  - `deleted_page`: URL no longer in sitemap
  - `ignored_file`: Image/document file (skipped)
- **Detection Date & Time**: When the change was detected
- **Details**: Human-readable description of the change
- **Previous Hash**: Previous content hash (for modified content)
- **New Hash**: New content hash (for new/modified content)
- **File Type**: File extension (for ignored files)

## CLI Options

The `export_changes_cli.py` script provides additional options:

- `--site, -s`: Export changes for specific site only
- `--date-range, -d`: Export changes from date range (e.g., 7d, 24h, 1w, 1m)
- `--output, -o`: Custom output filename
- `--list-sites`: List all available sites and exit
- `--verbose, -v`: Verbose output with file details

### Examples

```bash
# List available sites
python export_changes_cli.py --list-sites

# Export specific site
python export_changes_cli.py --site "Judiciary UK"

# Export changes from last 7 days
python export_changes_cli.py --date-range 7d

# Export with custom filename
python export_changes_cli.py --output "weekly_report.xlsx" --verbose
```

## Configuration

The script automatically uses your existing site configuration from `config/sites.yaml`. It will export changes for all active sites.

## Troubleshooting

### No Changes Found
If you see "No change files found for site", it means:
- No change detection has been run yet
- Change files are in a different location
- Site name doesn't match the configuration

### Missing Dependencies
If you get import errors:
```bash
pip install pandas openpyxl
```

### File Permissions
Ensure the script has write permissions to the `output/` directory.

## Example Output

The Excel file will look like this:

| Site: Judiciary UK | Detection Time: 2024-12-01 14:30:22 | Total Changes: 4 |
|-------------------|--------------------------------------|------------------|
| URL | Change Type | Detection Date & Time | Details | Previous Hash | New Hash | File Type |
| https://www.judiciary.uk/page1 | new_page | 2024-12-01 12:35:15 | New URL found in sitemap | | a1b2c3d4... | |
| https://www.judiciary.uk/page2 | modified_content | 2024-12-01 12:45:25 | Content hash changed from abc123... to def456... | abc123... | def456... | |

## Integration

This export functionality can be integrated into your workflow:

1. **Automated Reports**: Run after change detection completes
2. **Scheduled Exports**: Use cron/scheduler to generate daily/weekly reports
3. **API Integration**: Call the export script from your monitoring dashboard
4. **Email Reports**: Automatically email Excel reports to stakeholders

## Customization

You can customize the export by modifying the `ChangesExporter` class:

- **Styling**: Change colors, fonts, and formatting
- **Columns**: Add or remove data columns
- **Filtering**: Export only specific change types
- **Date Ranges**: Export changes from specific time periods 