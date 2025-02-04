
document.getElementById("client_2_contact_email").addEventListener("keyup", validateClient2Fields);
document.getElementById("client_2_address").addEventListener("keyup", validateClient2Fields);
document.getElementById("client_2_contact_phone").addEventListener("keyup", validateClient2Fields);

function validateClient2Fields() {
    let client2NameField = document.getElementById("client_2_name");
    let client2EmailField = document.getElementById("client_2_contact_email");
    let client2AddressField = document.getElementById("client_2_address");
    let client2PhoneField = document.getElementById("client_2_contact_phone");
    let errorMsg = document.getElementById("client_2_error_msg");

    let client2Name = client2NameField.value.trim();
    let client2Email = client2EmailField.value.trim();
    let client2Address = client2AddressField.value.trim();
    let client2Phone = client2PhoneField.value.trim();

    if ((client2Email.length > 0 || client2Address.length > 0 || client2Phone.length > 0) && client2Name.length === 0) {
        errorMsg.style.display = "block";  // Show the error message
    } else {
        errorMsg.style.display = "none";   // Hide the error message
    }
}

document.getElementById("client_1_contact_email").addEventListener("keyup", validateClient1Fields);
document.getElementById("client_1_address").addEventListener("keyup", validateClient1Fields);
document.getElementById("client_1_contact_phone").addEventListener("keyup", validateClient1Fields);

function validateClient1Fields() {
    let client1NameField = document.getElementById("client_1_name");
    let client1EmailField = document.getElementById("client_1_contact_email");
    let client1AddressField = document.getElementById("client_1_address");
    let client1PhoneField = document.getElementById("client_1_contact_phone");
    let errorMsg = document.getElementById("client_1_error_msg");

    let client1Name = client1NameField.value.trim();
    let client1Email = client1EmailField.value.trim();
    let client1Address = client1AddressField.value.trim();
    let client1Phone = client1PhoneField.value.trim();

    if ((client1Email.length > 0 || client1Address.length > 0 || client1Phone.length > 0) && client1Name.length === 0) {
        errorMsg.style.display = "block";  // Show the error message
    } else {
        errorMsg.style.display = "none";   // Hide the error message
    }
}

document.getElementById("client_3_contact_email").addEventListener("keyup", validateClient3Fields);
document.getElementById("client_3_address").addEventListener("keyup", validateClient3Fields);
document.getElementById("client_3_contact_phone").addEventListener("keyup", validateClient3Fields);

function validateClient3Fields() {
    let client3NameField = document.getElementById("client_3_name");
    let client3EmailField = document.getElementById("client_3_contact_email");
    let client3AddressField = document.getElementById("client_3_address");
    let client3PhoneField = document.getElementById("client_3_contact_phone");
    let errorMsg = document.getElementById("client_3_error_msg");

    let client3Name = client3NameField.value.trim();
    let client3Email = client3EmailField.value.trim();
    let client3Address = client3AddressField.value.trim();
    let client3Phone = client3PhoneField.value.trim();

    if ((client3Email.length > 0 || client3Address.length > 0 || client3Phone.length > 0) && client3Name.length === 0) {
        errorMsg.style.display = "block";  // Show the error message
    } else {
        errorMsg.style.display = "none";   // Hide the error message
    }
}

document.getElementById("client_4_contact_email").addEventListener("keyup", validateClient4Fields);
document.getElementById("client_4_address").addEventListener("keyup", validateClient4Fields);
document.getElementById("client_4_contact_phone").addEventListener("keyup", validateClient4Fields);

function validateClient4Fields() {
    let client4NameField = document.getElementById("client_4_name");
    let client4EmailField = document.getElementById("client_4_contact_email");
    let client4AddressField = document.getElementById("client_4_address");
    let client4PhoneField = document.getElementById("client_4_contact_phone");
    let errorMsg = document.getElementById("client_4_error_msg");

    let client4Name = client4NameField.value.trim();
    let client4Email = client4EmailField.value.trim();
    let client4Address = client4AddressField.value.trim();
    let client4Phone = client4PhoneField.value.trim();

    if ((client4Email.length > 0 || client4Address.length > 0 || client4Phone.length > 0) && client4Name.length === 0) {
        errorMsg.style.display = "block";  // Show the error message
    } else {
        errorMsg.style.display = "none";   // Hide the error message
    }
}

document.getElementById("client_5_contact_email").addEventListener("keyup", validateClient5Fields);
document.getElementById("client_5_address").addEventListener("keyup", validateClient5Fields);
document.getElementById("client_5_contact_phone").addEventListener("keyup", validateClient5Fields);

function validateClient5Fields() {
    let client5NameField = document.getElementById("client_5_name");
    let client5EmailField = document.getElementById("client_5_contact_email");
    let client5AddressField = document.getElementById("client_5_address");
    let client5PhoneField = document.getElementById("client_5_contact_phone");
    let errorMsg = document.getElementById("client_5_error_msg");

    let client5Name = client5NameField.value.trim();
    let client5Email = client5EmailField.value.trim();
    let client5Address = client5AddressField.value.trim();
    let client5Phone = client5PhoneField.value.trim();

    if ((client5Email.length > 0 || client5Address.length > 0 || client5Phone.length > 0) && client5Name.length === 0) {
        errorMsg.style.display = "block";  // Show the error message
    } else {
        errorMsg.style.display = "none";   // Hide the error message
    }
}

