/**
 * Authentication service allows HarriGT modules to make calls to endpoints that require a JWT
 */
(function() {
    'use strict';
  
    angular
      .module('app')
      .factory('authService', authService);

    /* @ngInject */
    function authService($http, $log, $localStorage, $rootScope){

        return {

            isAuthenticated: function(){
              return $localStorage.isAuthenticated || false;  
            },

            getUsername: function(){
                if (this.isAuthenticated()) {
                    return $localStorage.userProfile.username;
                }else{
                    return null;
                }
            },

            getAuthToken: function(){
                if (this.isAuthenticated()) {
                    return $localStorage.userProfile.token;
                }else{
                    return null;
                }
            },

            /**
             * Call POST endpoint to log in to API 
             */
            login: function(username, password){

                return $http.post('/login', {
                    "email": username,
                    "password": password
                  }).then(function(response){

                    console.log(response);

                    var result = response.data;

                    console.log("butts");

                    console.log(result);

                    $localStorage.isAuthenticated = (result.meta.code == 200);

                    if($localStorage.isAuthenticated) {
                        $localStorage.userProfile = result.response.user;
                        $localStorage.userProfile.username = username;
                    }

                    //alert subsystems to the fact that we signed in
                    $rootScope.$broadcast('user:loggedIn');

                    return $localStorage.isAuthenticated;
                  })
                  .catch(function(response){
                    console.log(response);
                    console.log("Whoopsie");
                    return false;
                  });

            },

            logout: function(){

                return $http.get("/logout")
                    .then(function(){
                        delete $localStorage.isAuthenticated;
                        delete $localStorage.userToken;
                        $rootScope.$broadcast('user:loggedOut');
                    });
            }
        };
    }



})();