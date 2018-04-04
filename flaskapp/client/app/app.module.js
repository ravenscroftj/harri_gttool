(function() {
  'use strict';

  angular
    .module('app', [
      // Angular libraries.
      'ngAnimate', 'ngSanitize', 'ngMessages', 'ngAria',
      // local storage library
      'ngStorage',
      // External libraries.
      'ui.router', 'ngMaterial',
      // Basic app blocks.
      'blocks.router',
      // Components,
      'app.components',
      // Feature modules.
      'app.auth', 'app.chat', 'app.search', 'app.news', 'app.news.article', 'app.header'
    ])
    .run(setGlobalState);

  /* @ngInject */
  function setGlobalState($rootScope, $state, $stateParams, $transitions, $mdMedia, $trace) {
    // It's very handy to add references to $state and $stateParams to the $rootScope
    // so that you can access them from any scope within your applications.For example,
    // <li ng-class="{ active: $state.includes('contacts.list') }"> will set the <li>
    // to active whenever 'contacts.list' or one of its descendants is active.
    $rootScope.$state = $state;
    $rootScope.$stateParams = $stateParams;
    $rootScope.isNavOpen = $mdMedia('gt-sm');

    $rootScope.toggleMenu = function(){
      $rootScope.isNavOpen = !$rootScope.isNavOpen;
    }

    // disable logging of transition states
    //$trace.enable('TRANSITION')

    // enable review process by default
    $rootScope.reviewProcessEnabled = false;
  }


})();
