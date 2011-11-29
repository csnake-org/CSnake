#ifndef FOUR_H
#define FOUR_H

// Exports
// This is a static lib, so don't import or export anything.
#define FOUR_EXPORT

#include <Three.h>

namespace math
{

/**
* Four
* Class that returns a mysterious number.
*/
class FOUR_EXPORT Four : public Three
{
public:
   Four();
   int getFour() const;
}; // class Four

} // namespace math

#endif // FOUR_H
