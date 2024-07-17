document.addEventListener("DOMContentLoaded", function () {
    const addRoleButton = document.getElementById("add-role-button");
    const newRoleRow = document.getElementById("new-role-row");
    const addRoleBtn = newRoleRow.querySelector(".add-role-btn");

    document.querySelectorAll('.delete-role-btn').forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            if (confirm('Are you sure you want to delete this role?')) {
                this.closest('form').submit();
            }
        });
    });
    document.querySelectorAll('.toggle-role-btn').forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const row = button.closest("tr");
            const status = row.querySelector(".Status-value").textContent.trim();
            const confirmationMessage = status === "Active" ? 
                "Are you sure you want to make this role Inactive?" : 
                "Are you sure you want to make this role Active?";
            if (confirm(confirmationMessage)) {
                this.closest('form').submit();
            }
        });
    });
    // Event listener for Add Role button
    addRoleButton.addEventListener("click", function () {
        newRoleRow.style.display = "table-row";
        addRoleButton.style.display = "none";
    });

    // Event listener for Add Role button inside the new role row
    addRoleBtn.addEventListener("click", function () {
        const name = document.querySelector("input[name='new-name']").value;
        const emailid = document.querySelector("input[name='new-emailid']").value;
        const number = document.querySelector("input[name='new-number']").value;
        const role = document.querySelector("select[name='new-role']").value;
        const clearance = document.querySelector("select[name='new-clearance']").value;
        const groups = document.querySelector("input[name='new-groups']").value;
        const psword = document.querySelector("input[name='new-psword']").value;
        const status = document.querySelector("select[name='new-status']").value;

        // Post the data using AJAX or form submission
        const formData = new FormData();
        formData.append("UserName", name);
        formData.append("email", emailid);
        formData.append("phoneNo", number);
        formData.append("Role", role);
        formData.append("Clearance", clearance);
        formData.append("groups", groups);
        formData.append("Passwords", psword);
        formData.append("Status", status);
        formData.append("username", "{{ user }}");

        fetch("/System_module/roles", {
            method: "POST",
            body: formData,
        })
            .then((response) => {
                if (response.ok) {
                    // Data posted successfully, you may want to reload the page or update the UI
                    location.reload(); // For example, reload the page to see the new role added
                } else {
                    throw new Error("Failed to add role");
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                // Handle error
            });

        // Hide the new role input row
        newRoleRow.style.display = "none";
        addRoleButton.style.display = "block";
    });

    const dropdown = document.getElementById("roleSelect");
    const clearTd = document.getElementById("clearTd");

    dropdown.addEventListener("change", function () {
        const role = dropdown.value;
        clearTd.innerHTML = "";

        let clearanceValue;

        // Set the clearance value based on the selected role
        if (role === "Admin") {
            clearanceValue = "3";
        } else if (role === "Maker") {
            clearanceValue = "1";
        } else if (role === "Approver") {
            clearanceValue = "2";
        }
        const clearanceSpan = document.createElement("span");
        clearanceSpan.textContent = clearanceValue;
        clearTd.appendChild(clearanceSpan);
    });
    
    const editButtons = document.querySelectorAll(".edit-btn");
    editButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const row = button.closest("tr");
            const usernameValue = row.querySelector(".UserName-value");
            const emailValue = row.querySelector(".email-value");
            const numberValue = row.querySelector(".phoneNo-value");
            const roleValue = row.querySelector(".Role-value");
            const clearanceValue = row.querySelector(".clearance-value");
            const groupsValue = row.querySelector(".groups-value");
            const passwordssValue = row.querySelector(".Passwords-value");
            const statusValue = row.querySelector(".Status-value");
            const updateBtn = row.querySelector(".update-btn");

            const usernameEdit = row.querySelector(".username-edit");
            const emailEdit = row.querySelector(".email-edit");
            const numberEdit = row.querySelector(".number-edit");
            const roleEdit = row.querySelector(".role-edit");
            const clearanceEdit = row.querySelector(".clearance-edit");
            const groupsEdit = row.querySelector(".groups-edit");
            const passwordssEdit = row.querySelector(".Password-edit");
            const statusEdit = row.querySelector(".status-edit");
            
            
            usernameEdit.value = usernameValue.textContent;
            emailEdit.value = emailValue.textContent;
            numberEdit.value = numberValue.textContent;
            roleEdit.value = roleValue.textContent;
            clearanceEdit.value = clearanceValue.textContent;
            groupsEdit.value = groupsValue.textContent;
            passwordssEdit.value = passwordssValue.textContent;
            statusEdit.value = statusValue.textContent;
        
            usernameValue.style.display = "none";
            emailValue.style.display = "none";
            numberValue.style.display = "none";
            roleValue.style.display = "none";
            clearanceValue.style.display = "none";
            groupsValue.style.display = "none";
            passwordssValue.style.display = "none";
            statusValue.style.display = "none";

            usernameEdit.style.display = "block";
            emailEdit.style.display = "block";
            numberEdit.style.display = "block";
            roleEdit.style.display = "block";
            clearanceEdit.style.display = "block";
            groupsEdit.style.display = "block";
            passwordssEdit.style.display = "block";
            statusEdit.style.display = "block";

            updateBtn.style.display = "block";
            button.style.display = "none";
        });
    });

    const updateButtons = document.querySelectorAll(".update-btn");
    updateButtons.forEach(function (button) {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            if (confirm("Are you sure you want to update this role?")) {
                const row = button.closest("tr");
                const usernameEdit = row.querySelector(".username-edit");
                const emailEdit = row.querySelector(".email-edit");
                const numberEdit = row.querySelector(".number-edit");
                const roleEdit = row.querySelector(".role-edit");
                const clearanceEdit = row.querySelector(".clearance-edit");
                const groupsEdit = row.querySelector(".groups-edit");
                const passwordssEdit = row.querySelector(".Password-edit");
                const statusEdit = row.querySelector(".status-edit");

                const formData = new FormData();
                formData.append("UserName", usernameEdit.value);
                formData.append("email", emailEdit.value);
                formData.append("phoneNo", numberEdit.value);
                formData.append("Role", roleEdit.value);
                formData.append("Clearance", clearanceEdit.value);
                formData.append("groups", groupsEdit.value);
                formData.append("Passwords", passwordssEdit.value);
                formData.append("Status", statusEdit.value);
                formData.append("username", "{{ user }}");

                fetch("/System_module/update/" + row.id.split("-")[1], {
                    method: "POST",
                    body: formData,
                })
                    .then((response) => {
                        if (response.ok) {
                            location.reload();
                        } else {
                            console.error("Failed to update role");
                        }
                    })
                    .catch((error) => {
                        console.error("Error:", error);
                    });
            }
        });
    });
});
