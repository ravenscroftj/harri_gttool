(function () {
    'use strict';

    angular
        .module('app.components')
        .directive('passwordVerify', passwordVerify);

    function passwordVerify() {
        return {
            restrict: 'A',
            require: '?ngModel',
            link: function (scope, elem, attrs, ngModel) {
                ngModel.$validators.myPwdInvalid = function (modelValue, viewValue) {
                    return viewValue === scope.$eval(attrs.passwordVerify);
                };
            }
        };
    }

})();
