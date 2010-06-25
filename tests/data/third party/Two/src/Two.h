#ifndef TWO_H
#define TWO_H

// Exports
#if (defined(_WIN32) || defined(WIN32))
#   ifdef TWO_EXPORTS
#       define TWO_EXPORT __declspec(dllexport)
#   else
#       define TWO_EXPORT __declspec(dllimport)
#   endif
#else
#   define TWO_EXPORT // unix needs nothing
#endif

namespace math
{

/**
* Two
* Class that returns a mysterious number.
*/
class TWO_EXPORT Two
{
public:
   Two();
   int getTwo() const;
private:
   int m_Two;
}; // class Two

} // namespace math

#endif // TWO_H
