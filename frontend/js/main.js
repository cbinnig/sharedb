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

function createPipelineForm(pipelines) {
    let form = document.getElementById("pipeline-form");

    let group = document.createElement("div");
    group.setAttribute("class", "form-group");
    form.appendChild(group);

    let select = document.createElement("select");
    select.setAttribute("id", "pipelineChoice");
    select.setAttribute("class", "form-control");
    group.appendChild(select);

    for (let name in pipelines) {
        if (pipelines.hasOwnProperty(name)) {
            let option = document.createElement("option");
            option.textContent = name + " - " + pipelines[name];
            option.setAttribute("value", name);
            select.appendChild(option);
        }
    }

    let submitButton = document.createElement("button");
    submitButton.setAttribute("type", "submit");
    submitButton.setAttribute("class", "btn btn-default");
    submitButton.textContent = "Set pipeline";
    form.appendChild(submitButton);
}

function createFilteringForm(ratings) {
    let form = document.getElementById("filter-form");

    for (let name in ratings) {
        if (ratings.hasOwnProperty(name)) {
            let group = document.createElement("div");
            group.setAttribute("class", "form-group");
            form.appendChild(group);

            let label = document.createElement("label");
            label.setAttribute("for", name + "FilterChoice");
            label.textContent = name;
            group.appendChild(label);

            let select = document.createElement("select");
            select.setAttribute("id", name + "FilterChoice");
            select.setAttribute("column", name);
            select.setAttribute("class", "form-control");
            group.appendChild(select);

            let ignore = document.createElement("option");
            ignore.textContent = "Ignore column";
            ignore.setAttribute("value", "ignore");
            select.appendChild(ignore);

            let best = "";
            // Tresholded
            let bestVal = 0.3;
            for (let cls in ratings[name]) {
                if (ratings[name].hasOwnProperty(cls)) {
                    if (ratings[name][cls] > bestVal) {
                        best = cls;
                        bestVal = ratings[name][cls];
                    }
                }
            }
            console.log(best);

            for (let cls in ratings[name]) {
                if (ratings[name].hasOwnProperty(cls)) {
                    let option = document.createElement("option");
                    option.textContent = cls + " - " + ratings[name][cls];
                    option.setAttribute("value", cls);
                    if (cls === best) {
                        option.selected = true;
                        select.value = cls;
                    }
                    select.appendChild(option);
                }
            }
        }
    }

    let submitButton = document.createElement("button");
    submitButton.setAttribute("type", "submit");
    submitButton.setAttribute("class", "btn btn-default");
    submitButton.textContent = "Filter columns";
    form.appendChild(submitButton);
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

function getPipelines(form) {
    $.get("api/pipeline", function(response) {
        if (response["ok"]) {
            createPipelineForm(response["pipelines"]);
        } else {
            presentAlert("alert-danger", "Unable to get available pipelines.");
        }
    });
    return false;
}

function setPipeline(form) {
    let data = {
        "pipeline": form.pipelineChoice.value,
    };

    $.post("api/pipeline", data, function(response) {
        if (response["ok"]) {
            presentAlert("alert-success", "Pipeline set to " + response["pipeline"]);
        } else {
            presentAlert("alert-danger", response["error"]);
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
            createFilteringForm(response["ratings"]);
        } else {
            presentAlert("alert-danger", "Unable to classify data");
        }
    });
    return false;
}

function filter(form) {
    let filters = {};
    let selections = form.getElementsByTagName("select");
    for (let i = 0; i < selections.length; i++) {
        let choice = selections[i].value;
        if (choice == "ignore") {
            continue;
        } else {
            filters[selections[i].getAttribute("column")] = choice;
        }
    }

    //let request = {
    //    "filters": filters,
    //};
    let request = filters;

    $.post("api/filter", request, function(response) {
        if (response["ok"]) {
            presentAlert("alert-success", "Table filtered");
            updateTable(response["table"], "#filtered");
        } else {
            presentAlert("alert-danger", "Unable to filter data")
        }
    });
    return false;
}

// Run on startup
$(document).ready(function(){
    showDHLogin();
});

function upload(form) {
    var repo_name = document.getElementById("repoName").value;
    var table_name = document.getElementById("tableName").value;
    var request = {"uploadTable" : form.uploadTable.value,
                   "repoName" : repo_name,
                   "tableName" : table_name};
    $.post("api/upload", request, function(response) {
        if (response["ok"]) {
            presentAlert("alert-success", "Filtered table uploaded");
        } else {
            presentAlert("alert-danger", "Unable to upload filtered table");
        }
    });
    return false;
}
