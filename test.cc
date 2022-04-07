template <class T>
struct vector {};

struct {
  int a : 4;
} b = {0}; //NOK auto
int c, d, e = 3, f, g, j, k, h; //NOK auto

namespace FrequencyRangeCDU {
struct FrequencyRangeD {};
}

vector<FrequencyRangeCDU::FrequencyRangeD> getDlFreqRangeList() {
    return {};
}

template<class T, class U>
void bar(U w) {
      T z = w.internal;
}

struct V {
  int n;
  int &r = n; //NOK auto
  int x = 456;  //NOK auto
};
thread_local inline V v = V();
extern V vv = V();
// extern V vv = V();
/*
    extern V vv = V();
*/

enum class E { a, b };
E x = E::a;

struct S
{
    int x;
    struct Foo
    {
        int i;
        int j = 321 + 123; // NOK
        int a[3];
    } b;
    const Foo123<> foo2 = Foo123(123); // NOK
    int foo() {
        char y = '5';  // OK
    }
};

struct A { int x; int y; int z; };

int main() {
    int a = 42, b = 123;
    int a = 42, b, c = 321; // NOK auto
    int x = *bla42() + 12;
    int x2 = *x1;
    int *ptr1 = &c;
    int *ptr2 = nullptr;  //NOK auto
    int *ptr3 = ptr2;
    const auto foo = 'c';
    const vector<FrequencyRangeCDU::FrequencyRangeD> dlFreqRangeList = getDlFreqRangeList();
    const char bar('c');
    const volatile char baz('c') ;
    const Foo123<> foo2 = Foo123(123);
    const Foo123<> foo3 = Foo123(123, 321);
    const Foo123<int> foo4 = Foo123<int>(dlFreqRangeList, 321);
    struct Foo { int i; } x = {0} ; //NOK auto
    int xx[] = { 1, 3, 5 }; //NOK auto
    char s[] = "abc"; //NOK auto
    int xxx = 42, y[5]; //NOK auto
    int b[5] = {0}; //NOK auto
    std::string str = "abc" + "efgh123" + getStr(321);
    char x = '4';// int x2 = *x1;
    char y = '5'; // OK

    int foobar(); // func declaration
    int foobar2{}; // ok variable, //NOK auto

    S s1 = { 1, { 2, 3, {4, 5, 6} } }; // aggregate initialization, NOK auto
    S s2 = { 1, 2, 3, 4, 5, 6}; // NOK auto
    A bb = {.x = 1, .z = 2}; // NOK auto
    STR("%s: availabilityStatus = %s, sequenceStatus = %s.", // NOK auto
    uint32_t left = 0; // OK with warning
    uint64_t left64 = 0; // OK with warning
    using super = request_frame; // NOK auto
    return 0;
}
