# DM Writer

Personalize cold DM sequences at scale. Reads leads from a local CSV file, researches each company (website + LinkedIn), and uses Gemini AI to write personalized 3-message DM sequences — then writes them back to the CSV.

## How It Works

1. Reads leads from your CSV (Company Name, Lead Name, Website, LinkedIn)
2. Scrapes each company's website and LinkedIn "About" page
3. Identifies likely pain points and goals from the research
4. Sends DM templates + research to Gemini to generate personalized messages
5. Writes personalized DM 1, DM 2, DM 3 back to the CSV

## Setup

### 1. Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create an API key

### 2. Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your `GEMINI_API_KEY`.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare Your CSV

Create a CSV file with these columns:

```csv
Company Name,Lead Name,Company Website,Company LinkedIn
Acme Corp,John Smith,https://acme.com,https://www.linkedin.com/company/acme
```

The tool will add **DM 1**, **DM 2**, **DM 3** columns automatically if they don't exist.

## Usage

### Basic Run

```bash
python main.py leads.csv
```

### Skip Rows with Existing DMs

```bash
python main.py leads.csv --skip-existing
```

### Dry Run (Preview Without Writing)

```bash
python main.py leads.csv --dry-run
```

### Custom Templates File

```bash
python main.py leads.csv --templates path/to/my_templates.txt
```

## Customizing DM Templates

Edit `templates/dm_templates.txt`. The file uses `---` as a separator between DMs:

```
DM 1
Your first message template here...

---

DM 2
Your follow-up template here...

---

DM 3
Your final follow-up template here...
```

Use placeholders like `{lead_name}`, `{company_name}`, `{pain_point}`, etc. — Gemini will replace them with personalized content based on company research.

## Notes

- **LinkedIn scraping**: LinkedIn may block automated requests. If a company's LinkedIn page can't be fetched, the tool falls back to website-only research.
- **Rate limiting**: The tool adds a 2-second delay between web requests to avoid being blocked.
- **Gemini model**: Uses `gemini-2.0-flash` by default. Change `GEMINI_MODEL` in `config.py` if needed.
