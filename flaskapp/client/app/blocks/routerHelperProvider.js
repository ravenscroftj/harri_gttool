(function() {
  'use strict';

  angular
    .module('blocks.router', [])
    .provider('routerHelper', routerHelperProvider);

  /* @ngInject */
  function routerHelperProvider($locationProvider, $stateProvider, $urlRouterProvider) {
    /* jshint validthis:true */
    this.$get = RouterHelper;

    $locationProvider.html5Mode(true);

    /* @ngInject */
    function RouterHelper($state) {
      var hasOtherwise = false;

      return {
        configureStates: configureStates,
        getStates: getStates
      };

      function configureStates(states, otherwisePath) {
        console.log("Configure router states");
        states.forEach(function(state) {
          $stateProvider.state(state.state, state.config);
        });
        if (otherwisePath && !hasOtherwise) {
          hasOtherwise = true;
          $urlRouterProvider.otherwise(otherwisePath);
        }
      }

      function getStates() {
        return $state.get();
      }
    }
  }

})();
