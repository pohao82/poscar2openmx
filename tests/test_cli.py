import os
import pytest

from poscar2openmx.cli import main
from conftest import V_POSCAR, keyword


def test_no_arguments_only_prints_hint(in_tmp, capsys):
    main([])
    assert os.listdir(in_tmp) == []
    out = capsys.readouterr().out
    assert 'No input file given' in out and '--example' in out


def test_example_copies_folder(in_tmp, capsys):
    main(['--example'])
    assert os.listdir(in_tmp) == ['input_example_HoAgGe']
    assert (in_tmp / 'input_example_HoAgGe' / 'params_file').exists()
    assert '--parameter_file params_file' in capsys.readouterr().out


def test_printed_commands_run(in_tmp, monkeypatch, capsys):
    main(['--example'])
    monkeypatch.chdir(in_tmp / 'input_example_HoAgGe')
    magmom = open('magmom_string').read()
    main(['hoagge.poscar.cart', '-o', 'a.dat'])
    main(['hoagge.poscar.cart', '--parameter_file', 'params_file'])
    main(['hoagge.poscar.cart', '--pol', 'nc', '--magmom', magmom, '-o', 'c.dat'])
    assert {'a.dat', 'openmx_input_file.dat', 'c.dat'} <= set(os.listdir('.'))


def test_example_does_not_overwrite(in_tmp, capsys):
    (in_tmp / 'input_example_HoAgGe').mkdir()
    (in_tmp / 'input_example_HoAgGe' / 'mine').write_text('keep')
    main(['--example'])
    assert os.listdir(in_tmp / 'input_example_HoAgGe') == ['mine']
    assert 'Skipped' in capsys.readouterr().out


def test_options_without_poscar():
    with pytest.raises(SystemExit) as e:
        main(['--pol', 'nc'])
    assert e.value.code == 2


def test_convert(in_tmp):
    main([V_POSCAR, '--pol', 'off', '--kgrid', '4', '4', '2', '-o', 'x.dat'])
    text = (in_tmp / 'x.dat').read_text()
    assert keyword(text, 'scf.SpinPolarization') == ['off']
    assert keyword(text, 'scf.Kgrid') == ['4', '4', '2']


def test_error_message(in_tmp):
    with pytest.raises(SystemExit) as e:
        main([V_POSCAR, '--element_order', 'V'])
    assert 'Error: element_order' in str(e.value.code)
