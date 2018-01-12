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
    $scope.loadingCandidates = false;
    $scope.showCandidatesView = true;
    $scope.showCandidateInfo = false;

    // When the state changes, the controller will be updated and a search will take place.
    $scope.$on('$stateChangeSuccess', function () {
      articleVm.loadFromState();
    });

    $scope.highlight = function(text, search) {
      if (!search) {
          return $sce.trustAsHtml(text);
      }
      return $sce.trustAsHtml(text.replace(new RegExp(search, 'gi'), '<span class="highlightedText">$&</span>'));
    };

    $scope.getPeople = function() {
      newsService.getPeople(articleVm.articleID).then(function(data){
        $scope.people=data;
      });
    };

    $scope.getInstitutions = function(){
      newsService.getInstitutions(articleVm.articleID).then(function(data){
        $scope.insts=data;
      });
    };

    $scope.viewCandidate = function(candidate){
      $scope.showCandidatesView = false;
      $scope.showCandidateInfo = true;
      $scope.candidate = candidate;
    };

    $scope.closeCandidateInspector = function(){
      $scope.showCandidatesView = true;
      $scope.showCandidateInfo = false;
    }

    /**
    * Handle button click from candidate link toggle button
    *
    */
    $scope.candidateLinkToggle = function(article, candidate){

      var promise = Promise.resolve()
      if(candidate.linked){

        promise = newsService.unlinkCandidate(article, candidate)

      }else{

        promise = newsService.linkCandidate(article, candidate)

      }

        promise.then(function(response){

            if(response.data.hasOwnProperty("id")){
                candidate.linked = true;
                candidate.linked_id = response.data.id
            }else{
              candidate.linked = false;
            }
            console.log(response.data);
            console.log(candidate);

            $scope.candidate.linked = candidate.linked;

            for(var i; i<$scope.candidates.length; i++){
              if ($scope.candidates[i].doi == candidate.doi){
                $scope.candidates[i].linked=candidate.linked;
                $scope.candidates[i].linked_id=candidate.linked_id;
              }
            }

        });

    }

    // Load local variables from the state (the URL of the page).
    function loadFromState() {

      $scope.loadingCandidates = true;

      newsService.getArticle(articleVm.articleID)
        .then(function(data){
          data.content = data.content.replace(/\n/g,"<br>");
          $scope.article = data
        });

      newsService.getCandidates(articleVm.articleID)
        .then(function(data){


          var candidates = [];

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

          $scope.candidates = candidates;
          $scope.candidateCount = candidates.length;

        }).then(newsService.getLinkedArticles(articleVm.articleID)
            .then(function(data){

              for(var i=0;i<data.length;i++){
                console.log(data[i]);

                for(var j=0;j<$scope.candidates.length;j++){
                  if($scope.candidates[j].doi == data[i].doi){
                    $scope.candidates[j].linked=true;
                    $scope.candidates[j].linked_id = data[i].id;
                  }
                }
              }

              //we're only done loading candidates once we get to this point
              $scope.loadingCandidates = false;;
          })
      );

    }
  }

})();
