
import fedoratagger.model as m

def dump2json():
    __version__ = '0.1'
    return dict(
        _format_version=__version__,
        packages=[package.__json__() for package in m.Package.query.all()],
        users=[user.__json__() for user in m.FASUser.query.all()],
    )


