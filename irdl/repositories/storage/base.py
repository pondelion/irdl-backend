from abc import ABCMeta, abstractmethod
from enum import Enum


class BaseStorageRepository(metaclass=ABCMeta):

    @abstractmethod
    def save(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_filelist(self, **kwargs):
        raise NotImplementedError
