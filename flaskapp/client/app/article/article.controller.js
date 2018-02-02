(function() {
  'use strict';

  angular
    .module('app.news.article', [])
    .constant('defaultTitle', 'News Article Matcher')
    .controller('ArticleController', ArticleController);

  /* @ngInject */
  function ArticleController($scope, $state, $sce, defaultTitle, newsService) {
    var articleVm = this;

    articleVm.title = defaultTitle;

    articleVm.articleID = $state.params.articleID;

    articleVm.loadFromState = loadFromState;

    $scope.candidates = [];
    $scope.hiding = false;

    $scope.showCandidatesView = true;
    $scope.showCandidateInfo = false;
    $scope.linkingCandidate = false;

    $scope.getPeople = function() {
      newsService.getPeople(articleVm.articleID).then(function(data){
        $scope.people=data;
      });
    };

    $scope.articleToggleHidden = function(article){

      var promise = Promise.resolve();
      $scope.hiding = true;

      if(article.hidden) {
        //unhide article
        promise = newsService.unhideArticle(article);
      }else{
        //hide article
        promise = newsService.hideArticle(article);
      }

      //resolve request then do next thing
      promise.then(function(response){
        $scope.article.hidden = response.data.hidden;
        $scope.hiding = false;
      });

    };


    $scope.articleToggleSpam = function(article){

      var promise = Promise.resolve();
      $scope.hiding = true;

      if(article.spam) {
        //unhide article
        promise = newsService.unspamArticle(article);
      }else{
        //hide article
        promise = newsService.spamArticle(article);
      }

      //resolve request then do next thing
      promise.then(function(response){
        $scope.article.spam = response.data.spam;
        $scope.hiding = false;
      });

    };

    $scope.getInstitutions = function(){
      newsService.getInstitutions(articleVm.articleID)
        .then(function(data){
          $scope.insts=data;
        })
        .then(function(){
          //get candidates - flush cache
          getCandidates(false);
        });

    };

    /**
    * Function called by datepicker for article publication datepicker
    *
    */
    $scope.changeArticleDate = function(){
      newsService.updateArticle($scope.article)
        .then(function(){
          getCandidates(false);
        });
    }

    $scope.viewCandidate = function(candidate){
      $scope.showCandidatesView = false;
      $scope.showCandidateInfo = true;
      $scope.candidate = candidate;
    };

    $scope.closeCandidateInspector = function(){
      $scope.showCandidatesView = true;
      $scope.showCandidateInfo = false;
    };

    /**
    * Handle button click from candidate link toggle button
    *
    */
    $scope.candidateLinkToggle = function(article, candidate){

      $scope.linkingCandidate = true;
      var promise = Promise.resolve();
      if(candidate.linked){

        promise = newsService.unlinkCandidate(article, candidate);

      }else{

        promise = newsService.linkCandidate(article, candidate);

      }

        promise.then(function(response){

            if(response.data.hasOwnProperty('id')){
                candidate.linked = true;
                candidate.linked_id = response.data.id;
            }else{
              candidate.linked = false;
            }
            console.log(response.data);
            console.log(candidate);

            $scope.candidate.linked = candidate.linked;

            for(var i; i<$scope.candidates.length; i++){
              if ($scope.candidates[i].doi === candidate.doi){
                $scope.candidates[i].linked=candidate.linked;
                $scope.candidates[i].linked_id=candidate.linked_id;
              }

              //set source to mskg if not known
              $scope.candidates[i]['_source'] = "mskg";
            }

            //finished (un)linking process
            $scope.linkingCandidate = false;

        });

    };

    function getCandidates(cached){

      $scope.candidateSearchMessage = "No Candidates Found";

      console.log("Article is currently:",$scope.article);
      $scope.loadingCandidates = true;

      if($scope.article){
          if(!$scope.article.publish_date){
            $scope.candidateCount = 0;
            $scope.candidateSearchMessage = "Set article publish date to search for candidates";
            $scope.loadingCandidates = false;
            return Promise.resolve();
          }
      }

      $scope.loadingCandidates = true;

      return newsService.getCandidates(articleVm.articleID, cached)
        .then(function(data){

          var candidates = [];

          if(data.candidate){
            for(var doi in data.candidate.doi2paper){
              var candidate = data.candidate.doi2paper[doi];
              candidate.doi = doi;

              if(!doi){
                candidate.score = data.candidate.doi_paper[candidate.Ti];
              }else{
                candidate.score = data.candidate.doi_paper[doi];
              }

              candidates.push(candidate);
            }
          }

          $scope.candidates = candidates;
          $scope.candidateCount = candidates.length;


          //we're only done loading candidates once we get to this point
          $scope.loadingCandidates = false;

          // return promise to caller
          return Promise.resolve();
        });
    }

    // Load local variables from the state (the URL of the page).
    function loadFromState() {

      var result = newsService.getArticle(articleVm.articleID)
      .then(function(data){
            data.content = data.content.replace(/\n/g,'<br>');

            console.log("Got article data");
            $scope.article = data;

            return Promise.resolve();
        }
      )
      .then(function(){
          console.log("Get candidates");
          return getCandidates();
      })
      .then(function(){
        console.log("Find links to articles")
        return newsService.getLinkedArticles(articleVm.articleID)
      })
      .then(function(data){
        console.log("Render links");
          for(var i=0;i<data.length;i++){
            console.log(data[i]);

            for(var j=0;j<$scope.candidates.length;j++){
              if($scope.candidates[j].doi == data[i].doi){
                $scope.candidates[j].linked=true;
                $scope.candidates[j].linked_id = data[i].id;
              }
            }
          }
      });
      console.log(result);
    }

    //load controller when it is opened
    loadFromState();
  }

})();
