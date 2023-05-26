#! /usr/bin/env python3
import atheris
import sys
import fuzz_helpers
import io
from contextlib import contextmanager


with atheris.instrument_imports(include=["simple_ddl_parser"]):
    from simple_ddl_parser import DDLParser, DDLParserError

ctr = 0
output_modes = ["mssql", "mysql", "oracle", "hql", "sql"]

@contextmanager
def nostdout():
    save_stdout = sys.stdout
    save_stderr = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    yield
    sys.stdout = save_stdout
    sys.stderr = save_stderr
def TestOneInput(data):
    global ctr
    ctr += 1
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    try:
        with nostdout():
            DDLParser(fdp.ConsumeRandomString()).run(json_dump=fdp.ConsumeBool(), output_mode=fdp.PickValueInList(output_modes), dump=fdp.ConsumeBool(), group_by_type=fdp.ConsumeBool())
    except DDLParserError:
        return -1
    except TypeError as e:
        if "string indices" in str(e) and ctr < 1000:
            return -1
        raise e
def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
