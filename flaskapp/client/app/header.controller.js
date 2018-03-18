(function() {
    'use strict';
  
    angular
      .module('app.header', [])
      .controller('HeaderCtrl', HeaderController);

  /* @ngInject */
  function HeaderController($scope, $rootScope, $state, $sce, authService) {

    console.log("Are we authed?:", authService.isAuthenticated());
    $scope.user = authService.getUsername();
    $rootScope.loggedIn = authService.isAuthenticated();

    $scope.$on("user:loggedIn", function(profile){

      $rootScope.loggedIn = true;
      $scope.user = authService.getUsername();

    });

    $scope.$on('user:loggedOut', function(){
      $rootScope.loggedIn = false;
      $scope.user = null;
    });

  }

})();