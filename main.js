// toggle between single date and date range fields
document.addEventListener("DOMContentLoaded", function () {
    var radios = document.querySelectorAll('input[name="prediction_type"]');
    var singleField = document.getElementById("single-field");
    var rangeFields = document.getElementById("range-fields");

    if (radios.length > 0) {
        radios.forEach(function (radio) {
            radio.addEventListener("change", function () {
                if (this.value === "range") {
                    singleField.style.display = "none";
                    rangeFields.style.display = "block";
                } else {
                    singleField.style.display = "block";
                    rangeFields.style.display = "none";
                }
            });
        });
    }

    // basic form validation
    var form = document.getElementById("predict-form");
    if (form) {
        form.addEventListener("submit", function (e) {
            var type = document.querySelector('input[name="prediction_type"]:checked').value;

            if (type === "single") {
                var dateVal = document.getElementById("date").value;
                if (!dateVal) {
                    e.preventDefault();
                    alert("Please select a date.");
                }
            } else {
                var startVal = document.getElementById("start_date").value;
                var endVal = document.getElementById("end_date").value;
                if (!startVal || !endVal) {
                    e.preventDefault();
                    alert("Please select both start and end dates.");
                } else if (startVal > endVal) {
                    e.preventDefault();
                    alert("Start date must be before end date.");
                }
            }
        });
    }
});


// render a line chart for predictions
function renderPredictionChart(canvasId, labels, datasets) {
    var ctx = document.getElementById(canvasId).getContext("2d");
    new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    title: { display: true, text: "Price" }
                },
                x: {
                    title: { display: true, text: "Date" }
                }
            },
            plugins: {
                legend: { position: "top" }
            }
        }
    });
}


// download table data as CSV
function downloadCSV(filename) {
    var table = document.getElementById("results-table");
    if (!table) return;

    var rows = table.querySelectorAll("tr");
    var csv = [];

    rows.forEach(function (row) {
        var cols = row.querySelectorAll("th, td");
        var rowData = [];
        cols.forEach(function (col) {
            rowData.push(col.innerText);
        });
        csv.push(rowData.join(","));
    });

    var blob = new Blob([csv.join("\n")], { type: "text/csv" });
    var link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename || "predictions.csv";
    link.click();
}
