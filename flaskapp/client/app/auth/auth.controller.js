(function() {
    'use strict';
  
    angular
      .module('app.auth', [])
      .controller('AuthController', AuthController);

  /* @ngInject */
  function AuthController($scope, $state, $sce, authService) {
        var authVm = this;

        $scope.loggingIn = false;
        $scope.authFailed = false;
        $scope.loggedOut = false;
        

        $scope.logout = function(){
            return authService.logout();
        };

        $scope.login = function(){
            
            $scope.loggingIn = true;
            $scope.authFailed = false;

            authService
                .login($scope.login.username, $scope.login.password)
                .then(function(isAuthenticated){
                    $scope.loggingIn = false;

                    if(isAuthenticated){
                        $state.go("main.news");
                    }else{
                        $scope.authFailed = true;
                    }
                });
        };


        function loadFromState(){

            if($state.current.name == "main.logout"){
                $scope.logout()
                .then(function(){
                    $scope.loggedOut = true;
                })
            }

        };


        // on initial execution, load state for login/logout behaviour
        loadFromState();
  }

})();