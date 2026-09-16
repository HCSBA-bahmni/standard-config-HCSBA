'use strict';

Bahmni.Registration.AttributesConditions.rules = {
    basicHealthInsurance: function (patient) {
        var result = {show: [], hide: []};
        var isapreConceptUuid = 'e8200001-0000-4000-8000-000000000002';
        var selectedConceptUuid = patient.basicHealthInsurance && patient.basicHealthInsurance.conceptUuid;

        if (selectedConceptUuid === isapreConceptUuid) {
            result.show.push('isapreInstitution');
        } else {
            patient.healthInsurer = undefined;
            result.hide.push('isapreInstitution');
        }
        return result;
    }
};
