let currentPage = 0;
document.addEventListener("DOMContentLoaded", function () {
    function submitForm() {
            const sliderbarValue = document.getElementById("sliderbarValue").value;
            const ruleSwitchValue = document.getElementById("ruleSwitchValue").checked;
            const aiSwitchValue = document.getElementById("aiSwitchValue").checked;

            const formData = {
                sliderbarValue: sliderbarValue,
                ruleSwitchValue: ruleSwitchValue ? 1 : 0,
                aiSwitchValue: aiSwitchValue ? 1 : 0
            };

            fetch("/rules_watchlist/sys", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(formData)
            })
            .then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    console.error("Failed to submit form");
                }
            })
            .catch(error => {
                console.error("Error:", error);
            });
    }

        // Update the slider value dynamically on input change
    document.getElementById("sliderbarValue").addEventListener("input", function() {
        const sliderValueSpan = document.getElementById("sliderValue");
        sliderValueSpan.textContent = this.value; // Update span with current slider value
    });

        // Prevent form submission and handle it through the submitForm function
    document.getElementById("submitSwitch").addEventListener("click", function(event) {
        event.preventDefault();
        submitForm();

    });
    document.getElementById('display_form_button').addEventListener('click', function () {
            var content = document.querySelector('.content1');
            if (content.style.display === 'none' || content.style.display === '') {
                content.style.display = 'block';
            } else {
                content.style.display = 'none';
            }
    });

    let isEditing = false;
    let addRuleButton = document.getElementById("add-rule-button");
    if (!addRuleButton) {
    addRuleButton = document.getElementById("add-rule-button1");
    }
    const newRuleRow = document.getElementById("new-rule-row");
    const addRuleBtn = newRuleRow.querySelector(".add-rule-btn");
    const operatorSelect = document.querySelector("select[name='new-operator']");
    const permissionDropdown = document.getElementById("permissionDropdown");

    const editButtons = document.querySelectorAll(".edit-btn");
    const updateButtons = document.querySelectorAll(".update-btn");
    const valueInputs = document.getElementById("valueInputs");


    const approveButton = document.getElementById('approve-button');
        const pendingButton = document.getElementById('pending-button');
        const declineButton = document.getElementById('decline-button');

        function setActiveButton(button) {
            button.classList.add('btn-active');
        }

        approveButton.addEventListener('click', function () {
            setActiveButton(approveButton);
            window.location.href = '/rules_watchlist/rules';
        });

        pendingButton.addEventListener('click', function () {
            setActiveButton(pendingButton);
            window.location.href = '/rules_watchlist/rules/pending';
        });

        declineButton.addEventListener('click', function () {
            setActiveButton(declineButton);
            window.location.href = '/rules_watchlist/rules/declined';
        });

        // Set the active button based on the current URL
        const currentUrl = window.location.pathname;
        if (currentUrl.endsWith('/pending')) {
            setActiveButton(pendingButton);
        } else if (currentUrl.endsWith('/declined')) {
            setActiveButton(declineButton);
        } else {
            setActiveButton(approveButton);
        }



    operatorSelect.addEventListener("change", function () {
        const selectedOperator = operatorSelect.value;
        if (selectedOperator === "in") {
            // Show the "Add More" button
            valueInputs.innerHTML = '<input type="text" class="form-control" name="new-value" placeholder="Value" required>';
            valueInputs.insertAdjacentHTML('beforeend', '<button type="button" class="btn btn-secondary add-value-btn"><i class="fas fa-plus" style="font-size: 1.2em;margin: 0% 28% 0% 5%;"></i>Add Values</button>');




            // Handle dynamic addition of value input fields
            const addValueButton = document.querySelector(".add-value-btn");
            addValueButton.addEventListener("click", function () {
                const valueInputGroup = document.createElement("div");
                valueInputGroup.className = "value-input-group";

                const newInput = document.createElement("input");
                newInput.type = "text";
                newInput.className = "form-control";
                newInput.name = "new-value";
                newInput.id = "extra-value-in";
                newInput.placeholder = "Value";

                const removeButton = document.createElement("button");
                removeButton.type = "button";
                removeButton.className = "btn btn-danger fas fa-trash-alt";
                removeButton.textContent = "";
                removeButton.addEventListener("click", function () {
                    valueInputGroup.parentNode.removeChild(valueInputGroup);
                });

                valueInputGroup.appendChild(newInput);
                valueInputGroup.appendChild(removeButton);

                // Insert the valueInputGroup before the addValueButton
                valueInputs.insertBefore(valueInputGroup, addValueButton);
            });
        }
        else if (selectedOperator === "in range"){
            valueInputs.innerHTML = '<input type="text" class="form-control" name="new-value" placeholder="MIN" required><input type="text" class="form-control" name="new-value" placeholder="MAX" required>';
        }

         else {
            // Hide the "Add More" button
            valueInputs.innerHTML = '<input type="text" class="form-control" name="new-value" placeholder="Value" required>';
        }
    });

    editButtons.forEach(function (button) {

    button.addEventListener("click", function () {
        if (isEditing) {
            return; // Do nothing if already editing
        }
        isEditing = true;
        const row = button.closest("tr");
        const columnValue = row.querySelector(".column-value");
        const operatorValue = row.querySelector(".operator-value");
        const channelValue = row.querySelector(".channel-value");
        const valueValue = row.querySelector(".value-value");
        const columnEdit = row.querySelector(".column-edit");
        const operatorEdit = row.querySelector(".operator-edit");
        const channelEdit = row.querySelector(".channel-edit");
        const valueEdit = row.querySelector(".edit-value");
        const updateBtn = row.querySelector(".update-btn");
        const valueInputs = row.querySelector(".value-inputs1"); // Assuming there's a container for value inputs within the row

        columnEdit.value = columnValue.textContent;
        operatorEdit.style.display = "none";
        valueEdit.value = valueValue.textContent;
        channelEdit.style.display = "none";
        // Toggle between display modes
        columnValue.style.display = "none";
        operatorValue.style.display = "none";
        channelValue.style.display= "none";
        valueValue.style.display = "none";
        columnEdit.style.display = "block";
        valueEdit.style.display = "block";
        updateBtn.style.display = "block";
        button.style.display = "none";

        // Create and populate operator dropdown
        const operatorSelect = document.createElement("select");
        operatorSelect.className = "form-control operator-edit";
        operatorSelect.style.display = "block";
        const operators = ["==", "!=", "<=", ">=", ">", "<", "in", "in range"];
        operators.forEach(function (op) {
            const option = document.createElement("option");
            option.value = op;
            option.textContent = op;
            operatorSelect.appendChild(option);
        });
        operatorSelect.value = operatorValue.textContent;
        operatorValue.parentNode.replaceChild(operatorSelect, operatorValue);

        const channelSelect = document.createElement("select");
        channelSelect.className = "form-control channel-edit";
        channelSelect.style.display = "block";
        const channels = ["ATM", "POS", "ECOM"];
        channels.forEach(function (ch) {
            const channel = document.createElement("option");
            channel.value = ch;
            channel.textContent = ch;
            channelSelect.appendChild(channel);
        });
        channelSelect.value = channelValue.textContent;
        channelValue.parentNode.replaceChild(channelSelect, channelValue);

        operatorSelect.addEventListener("change", function () {
            const selectedOperator = operatorSelect.value;
            let values;
                // Retrieve and display all values in the list
                try {
                     values = JSON.parse(valueEdit.value.replace(/\(/g, '[').replace(/\)/g, ']'));

                } catch {
                    // Handle JSON parsing error if needed
                    values = valueEdit.value
                }
            if (!Array.isArray(values)) {
                           values = [values];
               }

            if (selectedOperator === "in") {
                // Show the "Add More" button
                valueInputs.innerHTML = ''; // Clear the valueInputs div

                if (!values) {
                    values = [""];
                }


                values.forEach(function (value) {
                    const valueInputGroup = document.createElement("div");
                    valueInputGroup.className = "value-input-group";

                    const newInput = document.createElement("input");
                    newInput.type = "text";
                    newInput.className = "form-control";
                    newInput.name = "edit-value";
                    newInput.value = value;
                    newInput.placeholder = "Value";

                    const removeButton = document.createElement("button");
                    removeButton.type = "button";
                    removeButton.className = "btn btn-danger remove-value-btn";
                    removeButton.textContent = "Remove";
                    removeButton.addEventListener("click", function () {
                        valueInputGroup.parentNode.removeChild(valueInputGroup);
                    });

                    valueInputGroup.appendChild(newInput);
                    valueInputGroup.appendChild(removeButton);

                    // Insert the valueInputGroup
                    valueInputs.appendChild(valueInputGroup);
                });

                // Add a button to add more values
                valueInputs.insertAdjacentHTML('beforeend', '<button type="button" class="btn btn-secondary add-value-btn1"><i class="fas fa-plus" style="font-size: 1.2em;margin: 0% 28% 0% 5%;"></i>Add Values</button>');

                // Handle dynamic addition of value input fields
                const addValueButton = document.querySelector(".add-value-btn1");
                addValueButton.addEventListener("click", function () {
                    const valueInputGroup = document.createElement("div");
                    valueInputGroup.className = "value-input-group";

                    const newInput = document.createElement("input");
                    newInput.type = "text";
                    newInput.className = "form-control";
                    newInput.name = "edit-value";
                    newInput.placeholder = "Value";

                    const removeButton = document.createElement("button");
                    removeButton.type = "button";
                    removeButton.className = "btn btn-danger remove-value-btn";
                    removeButton.textContent = "Remove";
                    removeButton.addEventListener("click", function () {
                        valueInputGroup.parentNode.removeChild(valueInputGroup);
                    });

                    valueInputGroup.appendChild(newInput);
                    valueInputGroup.appendChild(removeButton);

                    // Insert the valueInputGroup before the addValueButton
                    valueInputs.insertBefore(valueInputGroup, addValueButton);
                });
            }
               else if (selectedOperator === "in range"){

                if (!values) {
                    valueInputs.innerHTML = '<input type="text" class="form-control" name="edit-value" placeholder="MIN" required ><input type="text" class="form-control" name="edit-value" placeholder="MAX" required>';
                }else{
                let html = ""
                if (values.length > 0) {
                      let min = Math.min(...values);
                      let max = Math.max(...values);
                      html += '<input type="text" class="form-control" name="edit-value" placeholder="MIN" value="' + min + '" required><input type="text" class="form-control" name="edit-value" placeholder="MAX" value="' + max + '" required>';
                }
//                values.slice(0, 2).forEach(function (value) {
//                     html += '<input type="text" class="form-control" name="edit-value" placeholder="MIN" value="' + value + '" required>';
//
//                    });
                               valueInputs.innerHTML = html
                 }
               }
            else
            {

                if (!values) {
                    valueInputs.innerHTML = '<input type="text" class="form-control" name="edit-value" placeholder="Value"  required>';
                }else{
                    valueInputs.innerHTML = '<input type="text" class="form-control" name="edit-value" placeholder="Value" value="' +values[0]  + '" required>';
                   }
            }
        });

        // Trigger change event to populate value inputs when the operator is already "in"
        if (operatorSelect.value === "in" || operatorSelect.value === "in range") {
            operatorSelect.dispatchEvent(new Event('change'));
        }

        else{
            valueEdit.value = JSON.parse(valueValue.textContent);
        }





    });
});

    updateButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            isEditing = false;
            const buttonId = button.id;

            const row = button.closest("tr");
            const columnEdit = row.querySelector(".column-edit");
            const operatorEdit = row.querySelector(".operator-edit");
            const channelEdit = row.querySelector(".channel-edit");
            const valueEdit = row.querySelector(".edit-value");
            const form = document.createElement("form");

            form.action = "/rules_watchlist/update/" + row.id.split("-")[1];
            form.method = "post";

            if(buttonId=='reupdate'){
                const columnInput = document.createElement("input");
                columnInput.type = "hidden";
                columnInput.name = "action";
                columnInput.value = 'reupdate';
                form.appendChild(columnInput);
            }



            // Create hidden input fields
            const columnInput = document.createElement("input");
            columnInput.type = "hidden";
            columnInput.name = "column_name";
            columnInput.value = columnEdit.value;
            form.appendChild(columnInput);
            

            const operatorInput = document.createElement("input");
            operatorInput.type = "hidden";
            operatorInput.name = "operator";
            operatorInput.value = operatorEdit.value;
            form.appendChild(operatorInput);

            const channelInput = document.createElement("input");
            channelInput.type = "hidden";
            channelInput.name = "channel";
            channelInput.value = channelEdit.value;
            form.appendChild(channelInput);



            let values;
            if (operatorEdit.value === "in") {
                // Collect all input values as a list
                const valueInputsList = document.querySelectorAll("input[name='edit-value']");
                values = JSON.stringify(Array.from(valueInputsList).map(input => input.value));
            }
             else if  (operatorEdit.value  === "in range"){
                values = document.querySelectorAll("input[name='edit-value']");
                values = Array.from(values).map(input => input.value);
                values = '(' + values.join(',') + ')';
            }

            else {
                try{
                values = JSON.stringify((valueEdit.value));
                }catch{}
                if (!values) {
                    values = JSON.stringify(document.querySelector("input[name='edit-value']").value);
                }

            }

            const valueInput = document.createElement("input");
            valueInput.type = "hidden";
            valueInput.name = "value";
            valueInput.value = values;
            form.appendChild(valueInput);

            const usernameInput = document.createElement("input");
            usernameInput.type = "hidden";
            usernameInput.name = "username";
            usernameInput.value = "{{ user }}";
            form.appendChild(usernameInput);

            document.body.appendChild(form);
            form.submit();
        });
    });

    addRuleButton.addEventListener("click", function () {
        newRuleRow.style.display = "table-row";
        addRuleButton.style.visibility = "hidden";
    });

    addRuleBtn.addEventListener("click", function () {
        const column_name = document.querySelector("select[name='new-column']").value;
        const operator = operatorSelect.value;
        let values;
        if (operator === "in") {
            // Collect all input values as a list
            const valueInputsList = document.querySelectorAll("input[name='new-value']");
            values = JSON.stringify(Array.from(valueInputsList).map(input => input.value));
        }
         else if  (operator === "in range"){
            values = document.querySelectorAll("input[name='new-value']");
            values = Array.from(values).map(input => input.value);
            values = '(' + values.join(',') + ')';
        }
         else {
            values = document.querySelector("input[name='new-value']").value;
        }
        const allpre = permissionDropdown.value;
        const channel = document.querySelector("select[name='new-channel']").value;
        // Post the data using AJAX or form submission
        // Example using AJAX:
        const formData = new FormData();
        formData.append("channel", channel);
        formData.append("column_name", column_name);
        formData.append("operator", operator);
        formData.append("value", values);
        formData.append("allpre", allpre);
        formData.append("username", "{{ user }}");
        fetch("/rules_watchlist/rules", {
            method: "POST",
            body: formData
        })
            .then(response => {
                if (response.ok) {
                    // Data posted successfully, you may want to reload the page or update the UI
                    location.reload(); // For example, reload the page to see the new rule added
                } else {
                    throw new Error("Failed to add rule");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                // Handle error
            });

        // Hide the new rule input row
        newRuleRow.style.display = "none";
        addRuleButton.style.visibility = "none";
    });



    //for blinking of the row and the pageination

    const objid = getQueryParam('objid');
    if (objid) {
        const row = document.getElementById(`rule-${objid}`);
        if (row) {
            row.classList.add('blink-row');
            const tbody = row.closest('tbody');
            const tbodyId = (tbody.id).match(/\d+/)[0];
            currentPage = parseInt(tbodyId);
        }
    }

    updatePaginationUI();
    showPage(currentPage);


});

function updatePaginationUI() {
    const pageButtonsContainer = document.getElementById('page-buttons');
    pageButtonsContainer.innerHTML = ''; // Clear existing buttons

    const maxVisiblePages = 5; // Number of page buttons visible at a time
    let startPage = Math.max(0, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages - 1, startPage + maxVisiblePages - 1);

    // Adjust startPage and endPage if currentPage is near the edges
    if (endPage - startPage < maxVisiblePages - 1) {
        startPage = Math.max(0, endPage - maxVisiblePages + 1);
    }

    // Create buttons for each visible page
    for (let i = startPage; i <= endPage; i++) {
        const button = document.createElement('button');
        button.textContent = i + 1;
        button.classList.add('pagination-button');
        button.onclick = function() {
            currentPage = i;
            showPage(currentPage);
        };
        pageButtonsContainer.appendChild(button);
    }
}

function showPage(page) {
    const pages = document.querySelectorAll('.page');
    pages.forEach((pageDiv, index) => {
        pageDiv.style.display = (index === page) ? 'table-row-group' : 'none';
    });
    const totalButtons = document.querySelectorAll('#pagination-controls button');
    totalButtons.forEach((button) => {
        button.textContent == page + 1 ? button.classList.add('active') : button.classList.remove('active');
    });
    totalButtons[0].disabled = (page === 0);
    totalButtons[1].disabled = (page === 0);
    totalButtons[totalButtons.length - 1].disabled = (page === totalPages - 1);
    totalButtons[totalButtons.length - 2].disabled = (page === totalPages - 1);
}

function goToFirstPage() {
    currentPage = 0;
    showPage(currentPage);
}

function goToLastPage() {
    currentPage = totalPages - 1;
    showPage(currentPage);
}

function nextPage() {
    if (currentPage < totalPages - 1) {
        currentPage++;
        showPage(currentPage);
    }
}

function previousPage() {
    if (currentPage > 0) {
        currentPage--;
        showPage(currentPage);
    }
}

function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}




