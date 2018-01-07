(function() {
  'use strict';

  angular
    .module('app.news')
    .factory('newsService', newsService);

  /* @ngInject */
  function newsService($http, $log) {

    var newsService = this;

    this.cache = {}

    return {

      getNews: getNews,

      getArticle: function(articleID){
        return getData('/api/news/' + articleID)
      },

      getPeople: function(articleID){
        return getData('/api/news/' + articleID + '/people')
      },

      getInstitutions: function(articleID){
        return getData('/api/news/' + articleID + '/institutions')
      }

    };

    function getData(url) {
      if(newsService.cache[url]){
        return new Promise(function(resolve, reject) {
          resolve(newsService.cache[url]);
        });
      }
      else{
        return $http.get(url)
          .then(function (response) {
            newsService.cache[url] = response.data;
            return response.data;
          })
          .catch(function (error) {
            $log.error('XHR failed for search. ' + error.data);
          });
      }
    }


    function getNews() {
      return $http.get('/api/news')
        .then(function (response) {
          return response.data;
        })
        .catch(function (error) {
          $log.error('XHR failed for search. ' + error.data);
        });
    }
  }

})();
