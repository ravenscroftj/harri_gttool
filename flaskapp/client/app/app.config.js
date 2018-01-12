(function() {
  'use strict';

  angular
    .module('app')
    .config(config);

  /* @ngInject */
  function config($compileProvider, $mdThemingProvider) {
    $compileProvider.aHrefSanitizationWhitelist(/^\s*(http|https):/);

    $mdThemingProvider.theme('successTheme')
    .primaryPalette('green');
  }

})();
