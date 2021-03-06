# Getting Started

### Pre-requisites

- clang-3.8 libclang-common-3.8-dev llvm-3.8 llvm-3.8-runtime
```bash
# On trusty
$ curl -sSL "http://apt.llvm.org/llvm-snapshot.gpg.key" | sudo -E apt-key add -
$ echo "deb http://apt.llvm.org/trusty/ llvm-toolchain-trusty-3.8 main" | sudo tee -a /etc/apt/sources.list > /dev/null
$ sudo apt-get update
$ sudo apt-get --no-install-suggests --no-install-recommends --force-yes install clang-3.8 libclang-common-3.8-dev llvm-3.8-runtime llvm-3.8
```

- Run `./install_deps.sh` for installing sanitizer coverage python script not distributed in ubuntu package (requires sudo)
- Requires test binary to be compiled with either `-fsanitize=address -fsanitize-coverage=<your_preference>` or `-fsanitize=undefined -fsanitize-coverage=<your_preference>` (you tell afl-sancov if its ASAN or UBSAN by passing `--sanitizer asan`, defaults to ubsan if flag not present in command line)
- Run afl-collect and collect all (or post triage) crashes to a directory called `unique` located under /path/to/afl/sync/dir, like so:
```bash
$ afl-collect -r afl-out afl-out/unique -- test_harness -i @@ -o /dev/null
```
Bear in mind that this directory name is to be passed to `--crash-dir` argument of afl-sancov
