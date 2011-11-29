#include "DummyClass2.h"

// in thirdParty
#include <Two.h>
#include <Three.h>
#include <Four.h>
// in thirdParty2
#include <Five.h>

namespace dummy
{

DummyClass2::DummyClass2() 
: m_count( 6 ) // warning: this value is used in the csnake test
{
	math::Two two;
	math::Three three;
	math::Four four;
	math::Five five;
    m_count += two.getTwo();
    m_count += three.getThree();
    m_count += four.getFour();
    m_count -= five.getFive();
}

int DummyClass2::getCount() const
{
   return m_count;
}

} // namespace dummy

