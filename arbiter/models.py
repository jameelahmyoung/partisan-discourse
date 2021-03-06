# arbiter.models
# Model definitions for the arbiter app.
#
# Author:   Benjamin Bengfort <bbengfort@districtdatalabs.com>
# Created:  Tue Aug 02 09:16:07 2016 -0400
#
# Copyright (C) 2016 District Data Labs
# For license information, see LICENSE.txt
#
# ID: models.py [cd70726] benjamin@bengfort.com $

"""
Model definitions for the arbiter app.
"""

##########################################################################
## Imports
##########################################################################

from django.db import models
from model_utils import Choices
from partisan.utils import nullable
from model_utils.models import TimeStampedModel
from picklefield.fields import PickledObjectField
from django.contrib.postgres.fields import ArrayField


##########################################################################
## Estimator Model
##########################################################################


class Estimator(TimeStampedModel):
    """
    Stores a Scikit-Learn Estimator object as a pickle in the database.
    """

    # Model types to help decide on evaluation criteria
    TYPES = Choices('classifier', 'regression', 'clusters', 'decomposition')

    model_type  = models.CharField(choices=TYPES, max_length=32) # The type of the estimator
    model_class = models.CharField(max_length=255, **nullable)   # The class name of the estimator
    model_form  = models.CharField(max_length=512, **nullable)   # The repr of the estimator
    estimator   = PickledObjectField(**nullable)                 # The pickled object model
    build_time  = models.DurationField(**nullable)               # The amount of time it took to buld
    owner       = models.ForeignKey('auth.User', **nullable)     # The owner, if any, of the model
    corpus      = models.ForeignKey('corpus.Corpus', **nullable) # The corpus the estimator was trained on

    class Meta:
        db_table = "estimators"
        get_latest_by = "created"

    def __str__(self):
        s =  "{} {} ({})".format(
            self.model_class, self.model_type.title(), self.created.strftime('%Y-%m-%d')
        )

        if self.owner:
            s += " for {}".format(self.owner)

        return s


class Score(TimeStampedModel):
    """
    Stores an evaluation metric for an estimator.
    """

    # Metrics define how a specific estimator is scored
    METRICS = Choices(
        'accuracy', 'auc', 'brier', 'f1', 'fbeta', 'hamming', 'hinge',
        'jaccard', 'logloss', 'mcc', 'precision', 'recall', 'roc', 'support',
        'mae', 'mse', 'mdae', 'r2',
        'rand', 'completeness', 'homogeneity', 'mutual', 'silhouette', 'v',
        'time',
    )

    metric    = models.CharField(choices=METRICS, max_length=32)    # The type of the score
    score     = models.FloatField(**nullable)                       # The actual value of the score
    label     = models.CharField(max_length=32, **nullable)         # The label, if any, of the score
    folds     = ArrayField(models.FloatField(), **nullable)         # Cross-validation scores
    estimator = models.ForeignKey(Estimator, related_name='scores') # The estimator being evaluated

    class Meta:
        db_table = "evaluations"
        get_latest_by = "created"

    def __str__(self):
        s = "{} score for {} = {:0.3f}".format(
            self.metric.title(), self.estimator, self.score
        )

        if self.label:
            s = "{} ".format(self.label.title()) + s

        return s
