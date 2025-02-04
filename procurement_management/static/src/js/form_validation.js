document.getElementById("tax_identification_number").addEventListener("keyup", function (event) {
    let tinField = document.getElementById("tax_identification_number");
    let errorMsg = document.getElementById("tin_error_msg");

    let tin = tinField.value.trim();
    let numericRegex = /^[0-9]+$/;

    if (tin.length !== 16 || !numericRegex.test(tin)) {
        errorMsg.style.display = "block";  // Show the error message
    } else {
        errorMsg.style.display = "none";   // Hide the error message
    }
});

document.getElementById("company_name").addEventListener("keyup", function (event) {
    let companyNameField = document.getElementById("company_name");
    let errorMsg = document.getElementById("company_name_error_msg");

    let companyName = companyNameField.value.trim();
    console.log("companyName");
    if (companyName.length == 0) {
        errorMsg.style.display = "block";  // Show the error message
    } else {
        errorMsg.style.display = "none";   // Hide the error message
    }
});

document.getElementById("company_registered_address").addEventListener("keyup", function (event) {
    let companyAddressField = document.getElementById("company_registered_address");
    let errorMsg = document.getElementById("company_registered_address_error_msg");

    let companyAddress = companyAddressField.value.trim();
    console.log("companyAddress");
    if (companyAddress.length == 0) {
        errorMsg.style.display = "block";  // Show the error message
    } else {
        errorMsg.style.display = "none";   // Hide the error message
    }
});

document.getElementById("trade_license_number").addEventListener("keyup", function (event) {
    let tradeLicenseField = document.getElementById("trade_license_number");
    let errorMsg = document.getElementById("trade_license_error_msg");

    let tradeLicense = tradeLicenseField.value.trim();
    let alphanumericRegex = /^[a-z0-9]+$/i;

    if (tradeLicense.length < 8 || tradeLicense.length > 20 || !alphanumericRegex.test(tradeLicense)) {
        errorMsg.style.display = "block";  // Show the error message
    } else {
        errorMsg.style.display = "none";   // Hide the error message
    }
});

document.getElementById("commencement_date").addEventListener("change", function (event) {
    let commencementDateField = document.getElementById("commencement_date");
    let errorMsg = document.getElementById("commencement_date_error_msg");
    // console.log("her");
    let commencementDate = new Date(commencementDateField.value);
    // print(commencementDate);
    let today = new Date();
    today.setHours(0, 0, 0, 0); // Set to the start of today

    if (commencementDate >= today) {
        errorMsg.style.display = "block";  // Show the error message
    } else {
        errorMsg.style.display = "none";   // Hide the error message
    }
});

document.getElementById("expiry_date").addEventListener("change", function (event) {
    let expiryDateField = document.getElementById("expiry_date");
    let errorMsg = document.getElementById("expiry_date_error_msg");

    let expiryDate = new Date(expiryDateField.value);
    let today = new Date();
    today.setHours(0, 0, 0, 0); // Set to the start of today

    if (expiryDate <= today) {
        errorMsg.style.display = "block";  // Show the error message
    } else {
        errorMsg.style.display = "none";   // Hide the error message
    }
});
/////////////////////////////////////////////////////////////////////////////////

// document.getElementById("file_input").addEventListener("change", function (event) {
//     let fileInput = document.getElementById("file_input");
//     let errorMsg = document.getElementById("file_error_msg");

//     let file = fileInput.files[0];
//     if (file && file.size > 1048576) { // Check if file size is greater than 1MB (1048576 bytes)
//         errorMsg.style.display = "block";  // Show the error message
//     } else {
//         errorMsg.style.display = "none";   // Hide the error message
//     }
// });