from django.http import HttpResponse


def index(request):
    vendors = [
        {"id": 1,  "name": "Ravi Kumar",       "phone": "+1 (555) 201-4823"},
        {"id": 2,  "name": "Priya Sharma",      "phone": "+1 (555) 374-9102"},
        {"id": 3,  "name": "John Mitchell",     "phone": "+1 (555) 489-6531"},
        {"id": 4,  "name": "Aisha Patel",       "phone": "+1 (555) 612-7748"},
        {"id": 5,  "name": "Carlos Fernandez",  "phone": "+1 (555) 730-2295"},
        {"id": 6,  "name": "Emily Zhang",       "phone": "+1 (555) 843-1167"},
        {"id": 7,  "name": "Omar Al-Rashid",    "phone": "+1 (555) 951-4402"},
        {"id": 8,  "name": "Sophie Müller",     "phone": "+1 (555) 102-8836"},
        {"id": 9,  "name": "Tanaka Hiroshi",    "phone": "+1 (555) 267-5519"},
        {"id": 10, "name": "Grace Okonkwo",     "phone": "+1 (555) 318-6074"},
        {"id": 11, "name": "Liam O'Brien",      "phone": "+1 (555) 424-9983"},
        {"id": 12, "name": "Natalia Ivanova",   "phone": "+1 (555) 539-3341"},
    ]

    total = len(vendors)

    rows_html = ""
    for v in vendors:
        rows_html += f"""
        <tr>
            <td style="
                padding: 14px 20px;
                border-bottom: 1px solid #f0f0f0;
                color: #6b7280;
                font-size: 14px;
                font-weight: 500;
                width: 80px;
            ">{v['id']}</td>
            <td style="
                padding: 14px 20px;
                border-bottom: 1px solid #f0f0f0;
                color: #111827;
                font-size: 14px;
                font-weight: 500;
            ">
                <div style="display:flex; align-items:center; gap:10px;">
                    <div style="
                        width: 36px;
                        height: 36px;
                        border-radius: 50%;
                        background: linear-gradient(135deg, #6366f1, #8b5cf6);
                        color: #fff;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 13px;
                        font-weight: 700;
                        flex-shrink: 0;
                    ">{v['name'][0].upper()}</div>
                    {v['name']}
                </div>
            </td>
            <td style="
                padding: 14px 20px;
                border-bottom: 1px solid #f0f0f0;
                color: #374151;
                font-size: 14px;
            ">{v['phone']}</td>
        </tr>
        """

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Vendor List</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                         Helvetica, Arial, sans-serif;
            background: #f3f4f6;
            min-height: 100vh;
            padding: 40px 24px;
        }}
        tr:hover td {{
            background: #f9fafb;
        }}
    </style>
</head>
<body>

    <!-- Page Header -->
    <div style="max-width: 860px; margin: 0 auto 28px auto;">
        <h1 style="
            font-size: 26px;
            font-weight: 700;
            color: #111827;
            letter-spacing: -0.4px;
        ">Vendors</h1>
        <p style="margin-top: 4px; color: #6b7280; font-size: 14px;">
            Manage and review all registered vendors.
        </p>
    </div>

    <!-- Card -->
    <div style="
        max-width: 860px;
        margin: 0 auto;
        background: #ffffff;
        border-radius: 14px;
        box-shadow: 0 1px 4px rgba(0,0,0,.08), 0 4px 16px rgba(0,0,0,.06);
        overflow: hidden;
    ">

        <!-- Card Top Bar -->
        <div style="
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px 24px;
            border-bottom: 1px solid #e5e7eb;
        ">
            <h2 style="font-size: 16px; font-weight: 600; color: #1f2937;">
                Vendor List
            </h2>

            <!-- Total Badge -->
            <div style="
                display: inline-flex;
                align-items: center;
                gap: 7px;
                background: #ede9fe;
                color: #6d28d9;
                padding: 6px 14px;
                border-radius: 999px;
                font-size: 13px;
                font-weight: 600;
            ">
                <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15"
                     viewBox="0 0 24 24" fill="none" stroke="currentColor"
                     stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
                Total Vendors: {total}
            </div>
        </div>

        <!-- Table -->
        <div style="overflow-x: auto;">
            <table style="
                width: 100%;
                border-collapse: collapse;
            ">
                <thead>
                    <tr style="background: #f9fafb;">
                        <th style="
                            padding: 12px 20px;
                            text-align: left;
                            font-size: 11px;
                            font-weight: 700;
                            text-transform: uppercase;
                            letter-spacing: 0.07em;
                            color: #9ca3af;
                            border-bottom: 1px solid #e5e7eb;
                            width: 80px;
                        ">ID</th>
                        <th style="
                            padding: 12px 20px;
                            text-align: left;
                            font-size: 11px;
                            font-weight: 700;
                            text-transform: uppercase;
                            letter-spacing: 0.07em;
                            color: #9ca3af;
                            border-bottom: 1px solid #e5e7eb;
                        ">Name</th>
                        <th style="
                            padding: 12px 20px;
                            text-align: left;
                            font-size: 11px;
                            font-weight: 700;
                            text-transform: uppercase;
                            letter-spacing: 0.07em;
                            color: #9ca3af;
                            border-bottom: 1px solid #e5e7eb;
                        ">Phone</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>

        <!-- Card Footer -->
        <div style="
            padding: 14px 24px;
            background: #f9fafb;
            border-top: 1px solid #e5e7eb;
            font-size: 13px;
            color: #9ca3af;
        ">
            Showing {total} of {total} vendors
        </div>

    </div>
</body>
</html>
"""

    return HttpResponse(html, content_type="text/html")
