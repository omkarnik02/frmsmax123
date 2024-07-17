document.addEventListener("DOMContentLoaded", function () {

    const addRoleButton = document.getElementById("add-config-button");
    const newRoleRow = document.getElementById("new-config-row");
    const addRoleBtn = newRoleRow.querySelector(".add-config-btn");
    const editButtons = document.querySelectorAll(".edit-btn");

    editButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const row = button.closest("tr");
            const channelValue = row.querySelector(".channel-value");
            const alertTypeValue = row.querySelector(".AlertType-value");
            const emailIdValue = row.querySelector(".EmailId-value");

            const channelEdit = row.querySelector(".channel-edit");
            const alertTypeEdit = row.querySelector(".AlertType-edit");
            const emailIdEdit = row.querySelector(".EmailId-edit");

            const updateBtn = row.querySelector(".update-btn");

            channelEdit.value = channelValue.textContent;
            alertTypeEdit.value = alertTypeValue.textContent;
            emailIdEdit.value = emailIdValue.textContent;

            // Toggle between display modes
            channelValue.style.display = "none";
            alertTypeValue.style.display = "none";
            emailIdValue.style.display = "none";

            channelEdit.style.display = "block";
            alertTypeEdit.style.display = "block";
            emailIdEdit.style.display = "block";

            updateBtn.style.display = "block";
            button.style.display = "none";
        });
    });

    const updateButtons = document.querySelectorAll(".update-btn");

    updateButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const row = button.closest("tr");
            const channelEdit = row.querySelector(".channel-edit");
            const alertTypeEdit = row.querySelector(".AlertType-edit");
            const emailIdEdit = row.querySelector(".EmailId-edit");

            const formData = new FormData();
            formData.append("Channel", channelEdit.value);
            formData.append("AlertType", alertTypeEdit.value);
            formData.append("EmailId", emailIdEdit.value);

            formData.append("username", "{{ user }}");

            fetch("/configure/update/" + row.id.split("-")[1], {
                method: "POST",
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    console.error("Failed to update config");
                }
            })
            .catch(error => {
                console.error("Error:", error);
            });
        });
    });

    addRoleButton.addEventListener("click", function () {
        newRoleRow.style.display = "table-row";
        addRoleButton.style.display = "none";
    });

    addRoleBtn.addEventListener("click", function () {
        const channel = document.querySelector("select[name='new-channel']").value;
        const alerttype = document.querySelector("input[name='new-AlertType']").value;
        const emailids = document.querySelector("input[name='new-EmailId']").value;

        const formData = new FormData();
        formData.append("Channel", channel);
        formData.append("AlertType", alerttype);
        formData.append("EmailId", emailids);

        formData.append("username", "{{ user }}");

        fetch("/configure/configs", {
            method: "POST",
            body: formData
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                throw new Error("Failed to add role");
            }
        })
        .catch(error => {
            console.error("Error:", error);
        });

        newRoleRow.style.display = "none";
        addRoleButton.style.display = "block";
    });
});
