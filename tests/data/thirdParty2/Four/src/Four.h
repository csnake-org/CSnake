#ifndef FOUR_H
#define FOUR_H

// Exports
// This is a static lib, so don't import or export anything.
#define FOUR_EXPORT

namespace math
{

/**
* Four
* Class that returns a mysterious number.
*/
class FOUR_EXPORT Four
{
public:
   Four();
   int getFour() const;
private:
   int m_Four;
}; // class Four

} // namespace math

#endif // FOUR_H
