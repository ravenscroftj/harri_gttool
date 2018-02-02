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

      updateArticle: updateArticle,

      linkCandidate: linkCandidate,

      unlinkCandidate: unlinkCandidate,

      unhideArticle: unhideArticle,

      hideArticle: hideArticle,

      spamArticle: spamArticle,

      unspamArticle: unspamArticle,

      getArticle: function(articleID){
        return getData('/api/news/' + articleID);
      },

      getPeople: function(articleID){
        return getData('/api/news/' + articleID + '/people');
      },

      getLinkedArticles: function(articleID){
        return getData('/api/news/' + articleID + '/links');
      },

      getInstitutions: function(articleID){
        return getData('/api/news/' + articleID + '/institutions');
      },

      getCandidates: function(articleID, cached){

        var c = "true";

        if(cached === false){
          c = "false";
        }

        return getData('/api/news/' + articleID + '/candidates?cached=' + c);
      }

    };

    /**
    * Remove hidden flag from given article
    *
    */
    function unhideArticle(article) {
        return $http.put('/api/news/' + article.id, {
          "hidden": "false"
        })
    }

    /**
    * Add hidden flag to article
    */
    function hideArticle(article) {
        return $http.put('/api/news/' + article.id, {
          "hidden": "true"
        })
    }

    /**
    * Remove spam flag from given article
    *
    */
    function unspamArticle(article) {
        return $http.put('/api/news/' + article.id, {
          "spam": "false"
        })
    }

    /**
    * Add spam flag to article
    */
    function spamArticle(article) {
        return $http.put('/api/news/' + article.id, {
          "spam": "true"
        })
    }

    function updateArticle(article) {
      return $http.put('/api/news/' + article.id, {
        "publish_date": article.publish_date
      })
    }

    /**
    * Remove link between a news article and a paper from database
    *
    */
    function unlinkCandidate(article, candidate) {
      return $http.delete('/api/news/' + article.id + '/links/' + encodeURI(candidate.linked_id))
      .catch(function (error){
        $log.error('XHR failed for save link ' + error.data);
      });
    }

    /**
    * Make an API call to link a news article to a candidate paper
    */
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


    function getNews(hidden,linked, spam, offset, filter) {

      return $http.get('/api/news', {"params":{
        "hidden": hidden,
        "linked": linked,
        "spam":spam,
        "offset":  offset,
        "urlfilter": filter
      }}).then(function (response) {
          return response.data;
        })
        .catch(function (error) {
          $log.error('XHR failed for search. ' + error.data);
        });
    }
  }

})();
