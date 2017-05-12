/**
 * Yay Javascript...
 * 
 * Make sure this is the last thing loaded in the <head> element.
 */
// Global variable
var TABLE_LIST;
// Utility functionality
function readCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

function eraseCookie(name) {
    // createCookie(name, "", -1);
    document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 UTC;";
}

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
  var alert = document.getElementById("globalAlert");
  showAlert();
  alert.innerHTML = message;
  alert.className = "alert " + style;
  setTimeout(hideAlert, 5000);
}

// View
function showDHLogin() {
    // Clear out old elements
    var div = document.getElementById("dh-login");
    while (div.hasChildNodes()) {
        div.removeChild(div.lastChild);
    }

    // Show the DataHub login button if required
    var token = readCookie("oauth_token");
    if (token == null) {
        // Write form
        var link = document.createElement("a");
        link.setAttribute("href", "/auth");
        var button = document.createElement("button");
        button.setAttribute("class", "btn btn-default");
        button.textContent = "Log in to DataHub";
        div.appendChild(link);
        link.appendChild(button);
    } else {
        // Set connection and display success
        startDH(token);
        div.textContent = "Logged in to DataHub!"
    }
}

function updateTable(table, target) {
    // Extract columns
    var columns = [];
    for (var key in table) {
        if (table.hasOwnProperty(key)) {
            columns.push(key);
        }
    }
    // Build data
    var size = table[columns[0]].length;
    var data = [];
    for (var i = 0; i < size; i++) {
        var row = [];
        for (var key of columns) {
            row.push(table[key][i]);
        }
        data.push(row);
    }
    // Reshape columns

    var stupidColumns = [];
    for (var name of columns) {
        stupidColumns.push({"title": name});
    }

    $(target).DataTable({
        "data": data,
        "columns": stupidColumns,
    });
}

function createPipelineForm(pipelines) {
    var form = document.getElementById("pipeline-form");

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
            var bestVal = 0.3;
            for (let cls in ratings[name]) {
                if (ratings[name].hasOwnProperty(cls)) {
                    if (ratings[name][cls] > bestVal) {
                        best = cls;
                        bestVal = ratings[name][cls];
                    }
                }
            }

            for (var cls in ratings[name]) {
                if (ratings[name].hasOwnProperty(cls)) {
                    var option = document.createElement("option");
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

    var submitButton = document.createElement("button");
    submitButton.setAttribute("type", "submit");
    submitButton.setAttribute("class", "btn btn-default");
    submitButton.textContent = "Filter columns";
    form.appendChild(submitButton);
}

// Datahub
function setTable(form) {
    var repoName = form.value;
    var tableName = document.getElementById('tableName');
    while (tableName.firstChild) {
        tableName.removeChild(tableName.firstChild);
    }
    for (var table in TABLE_LIST[repoName]) {
        var option = document.createElement("option");
        option.textContent = TABLE_LIST[repoName][table];
        tableName.appendChild(option);
    }
}

function setRepo() {
    var repoName = document.getElementById('repoName');
    var upRepoName = document.getElementById('upRepoName');
    for (var repo in TABLE_LIST) {
        var option = document.createElement("option");
        option.textContent = repo;
        var upOption = document.createElement("option");
        upOption.textContent = repo;
        repoName.appendChild(option);
        upRepoName.appendChild(upOption);
    }
    setTable(repoName);

}
function startDH(token) {
    var data = {"token": token};
    $.post("api/login", data, function(response) {
        if (response["ok"]) {
            presentAlert("alert-success", "DataHub connection successful");
            TABLE_LIST = response["table_list"];
            setRepo();
        } else {
            presentAlert("alert-danger", "Unable to login to DataHub");
           eraseCookie("oauth_token");
            showDHLogin();
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
    var data = {
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
    var data = {
        "repoName": form.repoName.value,
        "tableName": form.tableName.value,
        "sampleSize": form.sampleSize.value
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
    var filters = {};
    var selections = form.getElementsByTagName("select");
    for (var i = 0; i < selections.length; i++) {
        var choice = selections[i].value;
        if (choice == "ignore") {
            continue;
        } else {
            filters[selections[i].getAttribute("column")] = choice;
        }
    }

    //let request = {
    //    "filters": filters,
    //};
    var request = filters;

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
    var up_repo_name = document.getElementById("upRepoName").value;
    var table_name = document.getElementById("tableName").value;
    var request = {"uploadTable" : form.uploadTable.value,
                   "repoName" : repo_name,
                   "tableName" : table_name,
                   "up_repo_name" : up_repo_name};
    $.post("api/upload", request, function(response) {
        if (response["ok"]) {
            presentAlert("alert-success", "Filtered table uploaded");
        } else {
            presentAlert("alert-danger", "Unable to upload filtered table");
        }
    });
    return false;
}
