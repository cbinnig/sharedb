/**
 * Yay Javascript...
 * 
 * Make sure this is the last thing loaded in the <head> element.
 */

// Alert display
function setVisible(id) {
  document.getElementById(id).style.visibility = "visible";
}

function setHidden(id) {
  document.getElementById(id).style.visibility = "hidden";
}

function hideAlert() {
  document.getElementById("globalAlert").style.display = "none";
}

function showAlert() {
  document.getElementById("globalAlert").style.display = "block";
}

function presentAlert(style, message) {
  let alert = document.getElementById("globalAlert");
  showAlert();
  alert.innerHTML = message;
  alert.className = "alert " + style;
  setTimeout(hideAlert, 5000);
}

// View
function updateTable(table, target) {
    // Extract columns
    let columns = [];
    for (let key in table) {
        if (table.hasOwnProperty(key)) {
            columns.push(key);
        }
    }
    // Build data
    let size = table[columns[0]].length;
    let data = [];
    for (let i = 0; i < size; i++) {
        let row = [];
        for (let key of columns) {
            row.push(table[key][i]);
        }
        data.push(row);
    }
    // Reshape columns

    let stupidColumns = [];
    for (let name of columns) {
        stupidColumns.push({"title": name});
    }

    $(target).DataTable({
        "data": data,
        "columns": stupidColumns,
    });
}

// Datahub
function startDH(form) {
    let data = {"token": form.dhToken.value};
    $.post("api/login", data, function(response) {
        if (response["ok"]) {
            presentAlert("alert-success", "DataHub connection successful");
        } else {
            presentAlert("alert-danger", "Unable to login to DataHub");
        }
    });
    return false;
}

function queryTable(form) {
    let data = {
        "repoName": form.repoName.value,
        "tableName": form.tableName.value,
        "sampleSize": form.sampleSize.value,
    };

    $.post("api/query", data, function(response) {
        if (response["ok"]) {
            presentAlert("alert-success", "Table data retrieved");
            updateTable(response["table"], "#data");
        } else {
            presentAlert("alert-danger", "wat");
        }
    })

    return false;
}

function showRatings(ratings) {
    let columns = [{"title": "Class"}];
    let rows = [];
    for (let columnName in ratings) {
        if (ratings.hasOwnProperty(columnName)) {
            columns.push({"title": columnName});
            let scores = ratings[columnName];
            let i = 0;
            for (let rating in scores) {
                if (scores.hasOwnProperty(rating)) {
                    if (rows.length === i) {
                        rows.push([rating]);
                    }
                    rows[i].push(scores[rating]);
                    i += 1;
                }
            }
        }
    }
    $("#ratings").DataTable({
        "data": rows,
        "columns": columns,
        "paging": false,
        "search": false,
    });
}

function classify(form) {
    $.post("api/classify", {}, function(response) {
        if (response["ok"]) {
            presentAlert("alert-success", "Columns classified");
            showRatings(response["ratings"]);
        } else {
            presentAlert("alert-danger", "waaaattt");
        }
    });
    return false;
}

function filter(form) {
    $.post("api/filter", {}, function(response) {
        if (response["ok"]) {
            presentAlert("alert-success", "Table filtered");
            updateTable(response["table"], "#filtered");
        } else {
            presentAlert("alert-danger", "impossible")
        }
    });
    return false;
}