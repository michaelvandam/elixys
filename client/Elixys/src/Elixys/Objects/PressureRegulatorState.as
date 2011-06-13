package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class PressureRegulatorState extends JSONObject
	{
		// Constructor
		public function PressureRegulatorState(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type() != null) && (Type() != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		// Data wrappers
		public function Type():String
		{
			return super.flash_proxy::getProperty("type");
		}
		public function Number():uint
		{
			return parseInt(super.flash_proxy::getProperty("number"));
		}
		public function SetPressure():String
		{
			return super.flash_proxy::getProperty("setpressure");
		}
		public function ActualPressure():String
		{
			return super.flash_proxy::getProperty("actualpressure");
		}

		// Type
		static public var TYPE:String = "pressureregulatorstate";
	}
}
