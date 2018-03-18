(function() {
    'use strict';
  
    angular
      .module('app.header', [])
      .controller('HeaderCtrl', HeaderController);

  /* @ngInject */
  function HeaderController($scope, $state, $sce, authService) {

    console.log("Are we authed?:", authService.isAuthenticated());
    $scope.loggedIn = authService.isAuthenticated();
    $scope.user = authService.getUsername();

    $scope.$on("user:loggedIn", function(profile){

      $scope.loggedIn = true;
      $scope.user = authService.getUsername();

    });

    $scope.$on('user:loggedOut', function(){
      $scope.loggedIn = false;
      $scope.user = null;
    });

  }

})();