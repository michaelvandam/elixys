package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentTransfer extends Component
	{
		// Constructor
		public function ComponentTransfer(data:String = null, existingcontent:Object = null)
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
		public function get Target():uint
		{
			return parseInt(super.flash_proxy::getProperty("target"));
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

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			return JSONDataInteger("target", Target, false);
		}

		// Type
		static public var TYPE:String = "TRANSFER";
	}
}
