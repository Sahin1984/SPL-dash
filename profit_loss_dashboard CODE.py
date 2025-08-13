"""
Profit and Loss Dashboard
-------------------------

This module generates a self‑contained HTML dashboard for managing and
visualising a Statement of Profit or Loss. It encapsulates the core
functionality from a traditional command‑line interface into a modern,
interactive web page. The resulting page runs entirely in the browser
without requiring a Python backend once generated. Users can add,
edit and delete operations, see the results reflected instantly in
summary metrics and charts, and export the underlying data as a CSV
file.

The dashboard is inspired by the design of a menu‑driven attendance
management system (see accompanying screenshot) and features a
colourful button bar, status indicators and multiple charts. It
leverages Plotly’s JavaScript library (embedded directly in the
HTML) to render interactive charts offline. All computations are
performed client‑side using plain JavaScript.

Usage:

    python profit_loss_dashboard.py

Running this script will write ``profit_loss_dashboard.html`` into the
current directory (or the directory given by the ``--output``
argument). You can then open this file in any modern web browser to
interact with your profit and loss data.

Limitations:

    * Requires the ``plotly`` Python package to extract the
      JavaScript library. If Plotly is not installed, an exception
      will be raised when running this script.
    * The dashboard currently does not persist data between page
      reloads. If you refresh the page, any added/edited operations
      will be lost.

Author: Assistant (auto‑generated)
"""

import json
from pathlib import Path
from textwrap import dedent
from typing import List, Dict, Any

import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio


def get_plotlyjs() -> str:
    """Return the minified Plotly JS library as a string.

    Plotly does not expose a simple function to retrieve the library
    directly, but we can generate a dummy HTML document with
    ``include_plotlyjs='include'`` and then extract the contents of
    the second ``<script>`` tag where the library is embedded. This
    approach avoids relying on external CDN resources and keeps the
    dashboard completely offline.

    Returns:
        The contents of the Plotly library as a single string.
    """
    # Create a simple blank figure
    fig = go.Figure()
    # Generate HTML with the library included
    html = pio.to_html(fig, include_plotlyjs="include", full_html=False)
    # Split out the script tags
    parts = html.split("<script type=\"text/javascript\">")
    # The first script tag defines PlotlyConfig, the second is the
    # Plotly library; subsequent scripts define the empty figure.
    # We extract the second script's contents.
    if len(parts) < 3:
        raise RuntimeError("Unexpected structure when extracting Plotly JS")
    # The second part contains the library and ends with </script>
    lib_and_rest = parts[2]
    library, _ = lib_and_rest.split("</script>", 1)
    return library


def generate_dashboard_html(
    data: List[Dict[str, Any]],
    title: str,
    company: str,
    include_plotly: bool = True,
) -> str:
    """Construct the full HTML for the dashboard.

    Args:
        data: A list of dicts with keys 'Line', 'Amount' and 'Type'.
        title: The title of the statement (e.g., "Statement of Profit or Loss").
        company: The company name to display on the dashboard.

    Returns:
        A string containing the complete HTML document.
    """
    # Convert Python data into JSON for embedding into JS
    json_data = json.dumps(data, ensure_ascii=False)
    # Fetch the embedded Plotly library unless disabled
    plotly_js = get_plotlyjs() if include_plotly else ''

    # Prepare Plotly script tags depending on inclusion flag. When
    # `include_plotly` is false the configuration and library scripts
    # are omitted entirely. They are defined here so they can be
    # interpolated into the final HTML template.
    plotly_config_tag = (
        '<script type="text/javascript">\n'
        'window.PlotlyConfig = {MathJaxConfig: \"local\"};\n'
        '</script>'
        if include_plotly else ''
    )
    plotly_lib_tag = (
        '<script type="text/javascript">\n'
        f'{plotly_js}\n'
        '</script>'
        if include_plotly else ''
    )

    # CSS styles for the dashboard. We keep it minimal and self‑contained.
    # Colours are inspired by the screenshot provided by the user.
    css = dedent(
        """
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            background-color: #f5f7fa;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background-color: #2757b6;
            color: #fff;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }

        .header h1 {
            margin: 0;
            font-size: 24px;
            display: flex;
            align-items: center;
        }

        .header h1 span {
            margin-left: 10px;
            font-size: 18px;
            font-weight: normal;
        }

        .status-bar {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }

        .status-card {
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            padding: 15px;
            margin: 10px;
            flex: 1 1 200px;
            text-align: center;
        }

        .status-card h2 {
            margin: 0 0 5px;
            font-size: 16px;
            color: #2757b6;
        }

        .status-card p {
            margin: 0;
            font-size: 20px;
            font-weight: bold;
        }

        .button-bar {
            display: flex;
            justify-content: flex-start;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }

        .btn {
            flex: 1 1 180px;
            padding: 10px 15px;
            border: none;
            border-radius: 6px;
            color: #fff;
            font-size: 14px;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transition: background-color 0.2s ease;
        }

        .btn-revenue { background-color: #1cb55c; }
        .btn-cogs    { background-color: #f39c12; }
        .btn-income  { background-color: #8e44ad; }
        .btn-expense { background-color: #e74c3c; }
        .btn-export  { background-color: #16a085; }
        .btn-reset   { background-color: #7f8c8d; }

        .btn:hover {
            opacity: 0.9;
        }

        .section-title {
            font-size: 20px;
            margin: 30px 0 10px;
            color: #2757b6;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background-color: #fff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        th, td {
            padding: 10px;
            border-bottom: 1px solid #ecf0f1;
            text-align: left;
        }

        th {
            background-color: #f0f3f7;
            font-weight: bold;
            color: #2757b6;
        }

        tr:hover { background-color: #f9fbfc; }

        .actions {
            display: flex;
            gap: 5px;
        }

        .actions button {
            border: none;
            background: none;
            cursor: pointer;
            font-size: 14px;
            color: #2757b6;
        }

        .form-inline {
            display: flex;
            gap: 10px;
            margin: 15px 0;
            flex-wrap: wrap;
        }

        .form-inline input, .form-inline select {
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 14px;
        }

        .chart-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }

        .chart {
            flex: 1 1 300px;
            min-height: 300px;
        }

        .recommendations {
            background-color: #fff;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .recommendations ul {
            list-style-type: none;
            padding-left: 0;
            margin: 0;
        }

        .recommendations li {
            margin: 5px 0;
            font-size: 14px;
        }
        """
    )

    # JavaScript: core logic. It replicates the recalc and DataFrame
    # generation functions from the Python version in the browser.
    # Build the main JavaScript for dashboard functionality. We avoid
    # modern ES6 features such as arrow functions and template
    # literals to maximise compatibility and minimise the risk of
    # syntax errors in strict browsers. All braces are doubled to
    # escape f‑string interpolation.
    js = dedent(
        f"""
        // Embedded data from Python
        var data = {json_data};

        // Utility: format numbers as Azerbaijani currency (no decimals)
        function formatAmount(amount) {{
            var sign = amount < 0 ? '-' : '';
            var num = Math.abs(Math.round(amount));
            return sign + num.toString().replace(/\B(?=(\d{{3}})+(?!\d))/g, ' ');
        }}

        // Compute summary metrics
        function recalc(values) {{
            var sales = 0;
            var opening_inv = 0;
            var purchases = 0;
            var carriage_in = 0;
            var closing_inv = 0;
            var other_income = 0;
            var expenses = 0;
            for (var i = 0; i < values.length; i++) {{
                var item = values[i];
                var line = item.Line.toLowerCase();
                var amount = parseFloat(item.Amount) || 0;
                if (item.Type === 'Revenue') {{ sales += amount; }}
                else if (item.Type === 'COGS') {{
                    if (line.indexOf('opening') !== -1) {{ opening_inv += amount; }}
                    else if (line.indexOf('purchases') !== -1) {{ purchases += amount; }}
                    else if (line.indexOf('inwards') !== -1) {{ carriage_in += amount; }}
                    else if (line.indexOf('closing') !== -1) {{ closing_inv += amount; }}
                }} else if (item.Type === 'Other Income') {{ other_income += amount; }}
                else if (item.Type === 'Expense') {{ expenses += amount; }}
            }}
            var cost_of_sales = opening_inv + purchases + carriage_in - closing_inv;
            var gross_profit = sales - cost_of_sales;
            var net_income_before_exp = gross_profit + other_income;
            var profit_for_year = net_income_before_exp - expenses;
            return {{
                sales: sales,
                cost_of_sales: cost_of_sales,
                gross_profit: gross_profit,
                other_income: other_income,
                net_income_before_exp: net_income_before_exp,
                total_expenses: expenses,
                profit_for_year: profit_for_year
            }};
        }}

        // Update status cards
        function updateStatus(summary) {{
            document.getElementById('status-sales').textContent = formatAmount(summary.sales);
            document.getElementById('status-gross').textContent = formatAmount(summary.gross_profit);
            document.getElementById('status-net').textContent = formatAmount(summary.profit_for_year);
            var grossMargin = summary.sales > 0 ? (summary.gross_profit / summary.sales) * 100 : 0;
            var netMargin  = summary.sales > 0 ? (summary.profit_for_year / summary.sales) * 100 : 0;
            document.getElementById('status-gross-margin').textContent = grossMargin.toFixed(1) + '%';
            document.getElementById('status-net-margin').textContent = netMargin.toFixed(1) + '%';
        }}

        // Build the operations table
        function buildTable() {{
            var tbody = document.getElementById('operations-body');
            tbody.innerHTML = '';
            for (var idx = 0; idx < data.length; idx++) {{
                var item = data[idx];
                var tr = document.createElement('tr');
                var html = '';
                html += '<td>' + (idx + 1) + '</td>';
                html += '<td>' + item.Line + '</td>';
                html += '<td style="text-align:right">' + formatAmount(item.Amount) + '</td>';
                html += '<td>' + item.Type + '</td>';
                html += '<td class="actions">' +
                    '<button title="Edit" onclick="editOperation(' + idx + ')">✏️</button>' +
                    '<button title="Delete" onclick="deleteOperation(' + idx + ')">🗑️</button>' +
                    '</td>';
                tr.innerHTML = html;
                tbody.appendChild(tr);
            }}
        }}

        // Add new operation from form inputs
        function addOperation() {{
            var lineInput = document.getElementById('input-line');
            var amountInput = document.getElementById('input-amount');
            var typeInput = document.getElementById('input-type');
            var line = lineInput.value.trim();
            var amount = parseFloat(amountInput.value);
            var type = typeInput.value;
            if (!line || isNaN(amount)) {{
                alert('Please enter a valid description and amount.');
                return;
            }}
            data.push({{ Line: line, Amount: amount, Type: type }});
            lineInput.value = '';
            amountInput.value = '';
            typeInput.value = 'Revenue';
            refreshDashboard();
        }}

        // Delete an operation by index
        function deleteOperation(idx) {{
            if (!confirm('Delete this operation?')) return;
            data.splice(idx, 1);
            refreshDashboard();
        }}

        // Edit an operation: prompt user for new values
        function editOperation(idx) {{
            var item = data[idx];
            var newLine = prompt('Edit description:', item.Line);
            if (newLine === null) return;
            var newAmountStr = prompt('Edit amount:', item.Amount);
            if (newAmountStr === null) return;
            var newAmount = parseFloat(newAmountStr);
            if (isNaN(newAmount)) {{
                alert('Invalid amount');
                return;
            }}
            var newType = prompt('Edit type (Revenue, COGS, Other Income, Expense):', item.Type);
            if (newType === null) return;
            newType = newType.trim();
            if (['Revenue','COGS','Other Income','Expense'].indexOf(newType) === -1) {{
                alert('Invalid type');
                return;
            }}
            data[idx] = {{ Line: newLine.trim(), Amount: newAmount, Type: newType }};
            refreshDashboard();
        }}

        // Export data as CSV
        function exportCSV() {{
            var rows = ['Line,Amount,Type'];
            for (var i = 0; i < data.length; i++) {{
                var item = data[i];
                var lineEsc = '"' + item.Line.replace(/"/g, '""') + '"';
                rows.push(lineEsc + ',' + item.Amount + ',' + item.Type);
            }}
            // Join rows with a literal newline character. Double escaping
            // ensures the backslash survives through Python and
            // JavaScript string processing.
            var csvContent = rows.join('\\n');
            var blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
            var url = URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.setAttribute('href', url);
            a.setAttribute('download', 'profit_loss_data.csv');
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }}

        // Compute recommendations based on margins and ratios
        function computeRecommendations(summary) {{
            var recs = [];
            var grossMargin = summary.sales > 0 ? summary.gross_profit / summary.sales * 100 : 0;
            var netMargin = summary.sales > 0 ? summary.profit_for_year / summary.sales * 100 : 0;
            var expenseRatio = summary.sales > 0 ? summary.total_expenses / summary.sales * 100 : 0;
            var cogsRatio = summary.sales > 0 ? summary.cost_of_sales / summary.sales * 100 : 0;
            if (grossMargin < 20) recs.push('📌 Gross profit margin is low. Consider reducing cost of sales or increasing selling prices.');
            if (netMargin < 10) recs.push('📌 Net profit margin is below industry norms. Review pricing and cost structures.');
            if (expenseRatio > 70) recs.push('📌 Operating expenses are high relative to sales. Look for ways to streamline operations.');
            if (cogsRatio > 60) recs.push('📌 Cost of goods sold is consuming a large share of revenue. Negotiate better purchase terms or reduce waste.');
            if (recs.length === 0) recs.push('🎉 Financial performance is strong. Keep up the good work!');
            return recs;
        }}

        // Update all charts
        function updateCharts(summary) {{
            try {{
                var revenueData = [];
                var labels = [];
                var values = [];
                labels.push('Sales');
                values.push(summary.sales);
                labels.push('Other Income');
                values.push(summary.other_income);
                revenueData.push({{
                    values: values,
                    labels: labels,
                    type: 'pie',
                    marker: {{ colors: ['#1cb55c', '#8e44ad'] }}
                }});
                var revenueLayout = {{
                    title: 'Revenue Composition',
                    height: 350,
                    showlegend: true
                }};
                Plotly.newPlot('chart-revenue', revenueData, revenueLayout);
                var expLabels = [];
                var expValues = [];
                expLabels.push('Cost of Sales');
                expValues.push(summary.cost_of_sales);
                expLabels.push('Operating Expenses');
                expValues.push(summary.total_expenses);
                var expenseData = [{{
                    x: expLabels,
                    y: expValues,
                    type: 'bar',
                    marker: {{ color: ['#f39c12', '#e74c3c'] }}
                }}];
                var expenseLayout = {{
                    title: 'Expense Distribution',
                    height: 350,
                    yaxis: {{ title: 'Amount' }}
                }};
                Plotly.newPlot('chart-expense', expenseData, expenseLayout);
                var profitData = [{{
                    x: ['Sales', 'Gross Profit', 'Net Profit'],
                    y: [summary.sales, summary.gross_profit, summary.profit_for_year],
                    type: 'bar',
                    marker: {{ color: ['#1cb55c', '#27ae60', '#16a085'] }}
                }}];
                var profitLayout = {{
                    title: 'Profitability Overview',
                    height: 350,
                    yaxis: {{ title: 'Amount' }}
                }};
                Plotly.newPlot('chart-profit', profitData, profitLayout);
            }} catch (e) {{
                var ids = ['chart-revenue','chart-expense','chart-profit'];
                for (var j = 0; j < ids.length; j++) {{
                    var el = document.getElementById(ids[j]);
                    if (el) el.innerHTML = '';
                }}
            }}
        }}

        // Refresh the entire dashboard: table, status, charts, recommendations
        function refreshDashboard() {{
            var summary = recalc(data);
            buildTable();
            updateStatus(summary);
            updateCharts(summary);
            var recs = computeRecommendations(summary);
            var recContainer = document.getElementById('rec-list');
            recContainer.innerHTML = '';
            for (var i = 0; i < recs.length; i++) {{
                var li = document.createElement('li');
                li.textContent = recs[i];
                recContainer.appendChild(li);
            }}
        }}

        // On DOM ready, initialise dashboard
        document.addEventListener('DOMContentLoaded', function() {{
            var dbg = document.getElementById('debug');
            if (dbg) {{ dbg.textContent = 'JS loaded'; dbg.style.color = 'green'; }}
            document.getElementById('btn-add').addEventListener('click', addOperation);
            document.getElementById('btn-export').addEventListener('click', exportCSV);
            document.getElementById('btn-reset').addEventListener('click', function() {{
                if (!confirm('Reset all data to defaults?')) return;
                data = {json_data};
                refreshDashboard();
            }});
            refreshDashboard();
        }});
        """
    )

    # Compose the final HTML document
    html = dedent(
        f"""
        <!DOCTYPE html>
        <html lang="az">
        <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>{title} - {company}</title>
            <style>
            {css}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{title} <span>- {company}</span></h1>
                </div>
                <div class="status-bar">
                    <div class="status-card">
                        <h2>Total Sales</h2>
                        <p id="status-sales">0</p>
                    </div>
                    <div class="status-card">
                        <h2>Gross Profit</h2>
                        <p id="status-gross">0</p>
                    </div>
                    <div class="status-card">
                        <h2>Net Profit</h2>
                        <p id="status-net">0</p>
                    </div>
                    <div class="status-card">
                        <h2>Gross Margin</h2>
                        <p id="status-gross-margin">0%</p>
                    </div>
                    <div class="status-card">
                        <h2>Net Margin</h2>
                        <p id="status-net-margin">0%</p>
                    </div>
                </div>
                <div class="button-bar">
                    <button id="btn-add" class="btn btn-revenue">➕ Add Operation</button>
                    <button id="btn-export" class="btn btn-export">📁 Export CSV</button>
                    <button id="btn-reset" class="btn btn-reset">🔄 Reset Data</button>
                </div>
                <div class="form-inline">
                    <input id="input-line" type="text" placeholder="Description" style="flex:2" />
                    <input id="input-amount" type="number" step="0.01" placeholder="Amount" style="flex:1" />
                    <select id="input-type" style="flex:1">
                        <option value="Revenue">Revenue</option>
                        <option value="COGS">COGS</option>
                        <option value="Other Income">Other Income</option>
                        <option value="Expense">Expense</option>
                    </select>
                </div>
                <h2 class="section-title">Operations</h2>
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Description</th>
                            <th style="text-align:right">Amount</th>
                            <th>Type</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="operations-body"></tbody>
                </table>
                <h2 class="section-title">Charts</h2>
                <div class="chart-container">
                    <div id="chart-revenue" class="chart"></div>
                    <div id="chart-expense" class="chart"></div>
                    <div id="chart-profit" class="chart"></div>
                </div>
                <div class="recommendations">
                    <h3>Recommendations</h3>
                    <ul id="rec-list"></ul>
                </div>
                <!-- Debug indicator (hidden by default). This is used internally
                     during development to ensure that JavaScript executes. -->
                <div id="debug" style="display:none; margin-top:10px; color:red; font-weight:bold;">JS not loaded</div>
            </div>
            <!-- Scripts -->
            {plotly_config_tag}
            {plotly_lib_tag}
            <script type="text/javascript">
            {js}
            </script>
        </body>
        </html>
        """
    )
    return html


def main(output_dir: str = '.'):
    """Generate the dashboard HTML file and save it to disk.

    Args:
        output_dir: Directory where the HTML file should be written.
    """
    # Define the base data as per the existing command‑line tool
    data = [
        {"Line": "Sales (Satışlar)", "Amount": 200000, "Type": "Revenue"},
        {"Line": "Opening inventories (İlkin ehtiyatlar)", "Amount": 40000, "Type": "COGS"},
        {"Line": "Purchases (Alışlar)", "Amount": 110000, "Type": "COGS"},
        {"Line": "Carriage inwards (Gətirmə xərci)", "Amount": 20000, "Type": "COGS"},
        {"Line": "Closing inventories (Son ehtiyatlar)", "Amount": 50000, "Type": "COGS"},
        {"Line": "Sundry income (Digər gəlirlər)", "Amount": 5000, "Type": "Other Income"},
        {"Line": "Discounts receivable (Alınacaq endirimlər)", "Amount": 3000, "Type": "Other Income"},
        {"Line": "Rent (İcarə)", "Amount": 11000, "Type": "Expense"},
        {"Line": "Carriage outwards (Çatdırma xərci)", "Amount": 4000, "Type": "Expense"},
        {"Line": "Telephone (Telefon)", "Amount": 1000, "Type": "Expense"},
        {"Line": "Electricity (Elektrik)", "Amount": 2000, "Type": "Expense"},
        {"Line": "Wages and salaries (Əməkhaqqı və maaşlar)", "Amount": 9000, "Type": "Expense"},
        {"Line": "Depreciation (Amortizasiya)", "Amount": 7000, "Type": "Expense"},
        {"Line": "Irrecoverable debts (Ödənilməyən borclar)", "Amount": 3000, "Type": "Expense"},
        {"Line": "Motor expenses (Nəqliyyat xərcləri)", "Amount": 5000, "Type": "Expense"},
        {"Line": "Insurance (Sığorta)", "Amount": 1000, "Type": "Expense"}
    ]
    # Build the HTML
    html = generate_dashboard_html(data, title="Statement of Profit or Loss", company="ABC Şirkəti")
    # Determine output path
    out_path = Path(output_dir) / 'profit_loss_dashboard.html'
    out_path.write_text(html, encoding='utf-8')
    print(f"Dashboard successfully written to {out_path.resolve()}")


if __name__ == '__main__':
    main()