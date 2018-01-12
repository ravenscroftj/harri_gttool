(function() {
  'use strict';

  angular
    .module('app.news')
    .factory('newsService', newsService);

  /* @ngInject */
  function newsService($http, $log) {

    var newsService = this;

    this.cache = {};

    return {

      getNews: getNews,

      linkCandidate: linkCandidate,

      getArticle: function(articleID){
        return getData('/api/news/' + articleID)
      },

      getPeople: function(articleID){
        return getData('/api/news/' + articleID + '/people')
      },

      getInstitutions: function(articleID){
        return getData('/api/news/' + articleID + '/institutions')
      },

      getCandidates: function(articleID){
        return getData('/api/news/' + articleID + '/candidates')
      }

    };

    function linkCandidate(article, candidate){
        return $http.post('/api/news/' + article.id + '/links', {
          "candidate_doi": candidate.doi
        })
        .catch(function (error){
          $log.error('XHR failed for save link ' + error.data);
        });
    }

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
