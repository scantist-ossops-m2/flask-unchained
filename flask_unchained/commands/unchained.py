from flask_unchained import current_app
from flask_unchained.cli import click, with_appcontext

from ..utils import format_docstring
from .utils import print_table


@click.group('unchained')
def unchained_group():
    """
    Flask Unchained commands.
    """


@unchained_group.command()
@with_appcontext
def bundles():
    """
    List registered bundles.
    """
    header = ('Name', 'Location')
    rows = [(bundle.name, f'{bundle.__module__}.{bundle.__class__.__name__}')
            for bundle in current_app.unchained.bundles.values()]
    print_table(header, rows)


@unchained_group.command()
@click.argument('bundle_name', nargs=1, required=False, default=None,
                help='Only show options for a specific bundle.')
@with_appcontext
def config(bundle_name):
    """
    Show current app config (or optionally just the options for a specific bundle).
    """
    from ..hooks import ConfigureAppHook

    bundle = current_app.unchained.bundles[bundle_name] if bundle_name else None
    bundle_cfg = (ConfigureAppHook(None).get_bundle_config(bundle, current_app.env)
                  if bundle else None)

    header = ('Config Key', 'Value')
    rows = []
    for key, value in current_app.config.items():
        if not bundle or key in bundle_cfg:
            rows.append((key, str(value)))
    print_table(header, rows)


@unchained_group.command()
@with_appcontext
def extensions():
    """
    List extensions.
    """
    header = ('Name', 'Class', 'Location')
    rows = []
    for name, ext in current_app.unchained.extensions.items():
        ext = ext if not isinstance(ext, tuple) else ext[0]
        rows.append((name, ext.__class__.__name__, ext.__module__))
    print_table(header, sorted(rows, key=lambda row: row[0]))


@unchained_group.command()
@click.pass_context
def hooks(ctx):
    """
    List registered hooks (in the order they run).
    """
    from ..app_factory import AppFactory
    from ..hooks.run_hooks_hook import RunHooksHook

    unchained_config = AppFactory().load_unchained_config(ctx.obj.data['env'])
    _, bundles = AppFactory().load_bundles(getattr(unchained_config, 'BUNDLES', []))
    hooks = RunHooksHook(None).collect_from_bundles(bundles)

    header = ('Hook Name',
              'Default Bundle Module',
              'Bundle Module Override Attr',
              'Description')
    rows = [(hook.name,
             hook.bundle_module_name or '(None)',
             hook.bundle_override_module_name_attr or '(None)',
             format_docstring(hook.__doc__) or '(None)')
            for hook in hooks]
    print_table(header, rows)


@unchained_group.command()
@with_appcontext
def services():
    """
    List services.
    """
    header = ('Name', 'Class', 'Location')
    rows = []
    for name, svc in current_app.unchained.services.items():
        if not not hasattr(svc, '__name__') or not hasattr(svc, '__module__'):
            rows.append((name, str(svc), ''))
            continue
        rows.append((name,
                     svc.__class__.__name__ if isinstance(svc, object) else svc.__name__,
                     svc.__module__))
    print_table(header, sorted(sorted(rows, key=lambda row: row[0]), key=lambda row: row[2]))
