var normalizeChileanRun = function (value) {
    return String(value || "")
        .replace(/\./g, "")
        .replace(/-/g, "")
        .replace(/\s/g, "")
        .toUpperCase();
};

var formatChileanRun = function (value) {
    var normalized = normalizeChileanRun(value);
    if (!/^\d+[0-9K]$/.test(normalized)) {
        return String(value || "").trim().toUpperCase();
    }
    var body = normalized.slice(0, -1).replace(/^0+/, "");
    return (body || "0") + "-" + normalized.slice(-1);
};

var isValidChileanRun = function (value) {
    var normalized = normalizeChileanRun(value);
    if (!/^\d{1,8}[0-9K]$/.test(normalized)) {
        return false;
    }

    var body = normalized.slice(0, -1);
    if (/^0+$/.test(body)) {
        return false;
    }
    var suppliedCheckDigit = normalized.slice(-1);
    var factor = 2;
    var sum = 0;

    for (var index = body.length - 1; index >= 0; index -= 1) {
        sum += parseInt(body.charAt(index), 10) * factor;
        factor = factor === 7 ? 2 : factor + 1;
    }

    var remainder = 11 - (sum % 11);
    var expectedCheckDigit = remainder === 11 ? "0" : (remainder === 10 ? "K" : String(remainder));
    return suppliedCheckDigit === expectedCheckDigit;
};

var isValidEisMobilePhone = function (value) {
    return /^9[0-9]{8}$/.test(String(value || ""));
};

var isValidEisFixedPhone = function (value) {
    return /^[2-6][0-9]{8}$/.test(String(value || ""));
};

var isValidEisOtherPhone = function (value) {
    return /^(?:9|[2-6])[0-9]{8}$/.test(String(value || ""));
};

Bahmni.Registration.customValidator = {
    "age.days": {
        method: function (name, value) {
            return value >= 0;
        },
        errorMessage: "REGISTRATION_AGE_ERROR_KEY"
    },
    "Telephone Number": {
        method: function (name, value, personAttributeDetails) {
            return value && value.length> 6;
        },
        errorMessage: "REGISTRATION_TELEPHONE_NUMBER_ERROR_KEY"
    },
    "RUN": {
        method: function (name, value) {
            return !value || isValidChileanRun(value);
        },
        normalize: formatChileanRun,
        errorMessage: "REGISTRATION_RUN_INVALID_KEY"
    },
    "phoneNumber": {
        method: function (name, value) {
            return isValidEisMobilePhone(value);
        }
    },
    "fixedPhoneNumber": {
        method: function (name, value) {
            return isValidEisFixedPhone(value);
        }
    },
    "alternatePhoneNumber": {
        method: function (name, value) {
            return isValidEisOtherPhone(value);
        }
    },
    "caste": {
        method: function (name, value, personAttributeDetails) {
            return value.match(/^\w+$/);
        },
        errorMessage: "REGISTRATION_CASTE_TEXT_ERROR_KEY"
    }
};
