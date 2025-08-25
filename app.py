from flask import Flask, request, render_template_string
import requests
import datetime

app = Flask(__name__)

def format_timestamp(unix_ts):
    try:
        if unix_ts and unix_ts > 0:
            return datetime.datetime.fromtimestamp(unix_ts).strftime("%Y-%m-%d %H:%M")
        else:
            return "N/A"
    except:
        return "Invalid Date"

def get_event_data(region='(ind'):
    url = f'https://narayan-event.vercel.app/event?region={region}'
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; WebApp/1.0)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Events - {{ region.upper() }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body {
            font-family: "Segoe UI", sans-serif;
            margin: 0;
            padding: 2rem;
            background-color: #f0f2f5;
            color: #222;
            transition: background-color 0.3s, color 0.3s;
        }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }
        h1 {
            margin: 0;
        }
        .toggle-btn {
            background: none;
            border: 1px solid #888;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
        }
        form {
            margin-bottom: 2rem;
        }
        input[type="text"] {
            padding: 8px;
            font-size: 1rem;
            width: 200px;
            margin-right: 10px;
        }
        button {
            padding: 8px 14px;
            font-size: 1rem;
            cursor: pointer;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
        }
        .event {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .event img {
            width: 100%;
            height: 180px;
            object-fit: cover;
        }
        .event .content {
            padding: 1rem;
        }
        .event h2 {
            font-size: 1.2rem;
            margin: 0 0 0.5rem;
        }
        .event p {
            margin: 0.5rem 0;
        }
        .link-btn {
            margin-top: auto;
            padding: 0.5rem;
            text-align: center;
            background-color: #0077cc;
            color: white;
            text-decoration: none;
            display: block;
            border-top: 1px solid #eee;
        }

        .dark {
            background-color: #121212;
            color: #eee;
        }

        .dark .event {
            background-color: #1e1e1e;
            color: #ccc;
        }

        .dark .link-btn {
            background-color: #3380cc;
        }
    </style>
</head>
<body>
<header>
    <h1>🌍 Here Are The New Events Of {{ region.upper() }}</h1>
    <button class="toggle-btn" onclick="toggleDark()">🌓 Dark Mode</button>
</header>

<form method="get" action="/">
    <input type="text" name="region" value="{{ region }}" placeholder="Enter region" />
    <button type="submit">Fetch Events</button>
</form>

{% if error %}
    <p style="color: red;">{{ error }}</p>
{% elif events %}
    <div class="grid">
        {% for event in events %}
            <div class="event">
                <img src="{{ event.Banner or 'https://via.placeholder.com/600x200?text=No+Image' }}" alt="Banner" />
                <div class="content">
                    <h2>{{ event.Title }}</h2>
                    <p><strong>Start:</strong> {{ event.StartFormatted }}</p>
                    <p><strong>End:</strong> {{ event.EndFormatted }}</p>
                    <p>{{ event.Details }}</p>
                </div>
                {% if event.link %}
                    <a href="{{ event.link }}" class="link-btn" target="_blank">🔗 More Info</a>
                {% endif %}
            </div>
        {% endfor %}
    </div>
{% else %}
    <p>No events found for this region.</p>
{% endif %}

<script>
    // On load: Apply saved dark mode setting
    document.addEventListener("DOMContentLoaded", () => {
        const mode = localStorage.getItem("darkMode");
        if (mode === "enabled") {
            document.body.classList.add("dark");
        }
    });

    // Toggle dark mode and save preference
    function toggleDark() {
        const isDark = document.body.classList.toggle("dark");
        localStorage.setItem("darkMode", isDark ? "enabled" : "disabled");
    }
</script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    region = request.args.get('region', 'th').lower()
    region = ''.join(c for c in region if c.isalnum())  # Basic sanitization

    data = get_event_data(region)

    if data is None:
        return render_template_string(HTML_TEMPLATE, region=region, events=None, error="Failed to fetch event data.")
    
    if isinstance(data, list):
        events = data
    elif isinstance(data, dict):
        events = data.get("events") or data.get("Events") or []
    else:
        events = []

    cleaned_events = []
    for e in events:
        title = e.get("Title") or e.get("title") or "Untitled Event"
        details = e.get("Details") or e.get("details") or "No details available."
        start = e.get("Start") or 0
        end = e.get("End") or 0
        link = e.get("link") or e.get("Link") or ""
        banner = e.get("Banner") or e.get("banner") or ""

        cleaned_events.append({
            "Title": title,
            "Details": details.strip(),
            "StartFormatted": format_timestamp(start),
            "EndFormatted": format_timestamp(end),
            "link": link,
            "Banner": banner,
        })

    return render_template_string(HTML_TEMPLATE, region=region, events=cleaned_events, error=None)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
