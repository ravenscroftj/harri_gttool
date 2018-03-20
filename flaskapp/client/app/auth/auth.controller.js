(function() {
    'use strict';
  
    angular
      .module('app.auth', [])
      .controller('AuthController', AuthController);

  /* @ngInject */
  function AuthController($scope, $rootScope, $state, $sce, authService) {
        var authVm = this;

        $scope.loggingIn = false;
        $scope.authFailed = false;
        $scope.loggedOut = false;
        $rootScope.loggedIn = false;
        $rootScope.registered = false;

        $scope.logout = function(){
            return authService.logout();
        };

        $scope.register = function(){
            var formdata = {
                "email": $scope.email,
                "password": $scope.password,
                "password_confirm": $scope.password2,
                "full_name": $scope.fullname
            }

            authService.register(formdata)
                .catch(function(response){
                    $scope.errorMessages = response.data.response.errors;
                })
                .then(function(result){
                    console.log(result);
                });
        }

        $scope.login = function(){
            
            $scope.loggingIn = true;
            $scope.authFailed = false;

            authService
                .login($scope.login.username, $scope.login.password)
                .then(function(isAuthenticated){
                    $scope.loggingIn = false;

                    if(isAuthenticated){
                        $rootScope.loggedIn = true;
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
                    $rootScope.loggedIn = false;
                    $scope.loggedOut = true;
                })
            }

        };


        // on initial execution, load state for login/logout behaviour
        loadFromState();
  }

})();