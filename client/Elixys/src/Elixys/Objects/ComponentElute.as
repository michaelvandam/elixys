package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentElute extends Component
	{
		// Constructor
		public function ComponentElute(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Data wrappers
		public function get Reagent():uint
		{
			return super.flash_proxy::getProperty("reagent");
		}
		public function set Reagent(value:uint):void
		{
			super.flash_proxy::setProperty("reagent", value);
		}
		
		public function get ReagentDescription():String
		{
			return super.flash_proxy::getProperty("reagentdescription");
		}
		public function set ReagentDescription(value:String):void
		{
			super.flash_proxy::setProperty("reagentdescription", value);
		}

		public function get ReagentValidation():String
		{
			return super.flash_proxy::getProperty("reagentvalidation");
		}
		public function set ReagentValidation(value:String):void
		{
			super.flash_proxy::setProperty("reagentvalidation", value);
		}

		public function get Target():uint
		{
			return super.flash_proxy::getProperty("target");
		}
		public function set Target(value:uint):void
		{
			super.flash_proxy::setProperty("target", value);
		}
		
		public function get TargetDescription():String
		{
			return super.flash_proxy::getProperty("targetdescription");
		}
		public function set TargetDescription(value:String):void
		{
			super.flash_proxy::setProperty("targetdescription", value);
		}
		
		public function get TargetValidation():String
		{
			return super.flash_proxy::getProperty("targetvalidation");
		}
		public function set TargetValidation(value:String):void
		{
			super.flash_proxy::setProperty("targetvalidation", value);
		}

		// Type
		static public var TYPE:String = "ELUTE";
	}
}
