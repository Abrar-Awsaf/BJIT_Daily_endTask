
const fileFields = [
    'trade_license_business_registration', 'certificate_of_incorporation', 'certificate_of_good_standing',
    'establishment_card', 'vat_tax_certificate', 'memorandum_of_association',
    'identification_document_for_authorized_person', 'bank_letter_indicating_bank_account',
    'past_2_years_audited_financial_statements', 'other_certifications'
];

fileFields.forEach(field => {
    document.getElementById(field).addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file && file.size > 1048576) { // 1 MB in bytes
            alert('File size should not exceed 1 MB');
            event.target.value = ''; // Clear the input
        }
    });
});